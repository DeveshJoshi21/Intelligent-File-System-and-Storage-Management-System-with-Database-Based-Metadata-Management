import os,hashlib
from datetime import datetime
from .db import get_db
SKIP={".git","__pycache__",".venv","venv","node_modules"}
def stamp(): return datetime.now().astimezone().isoformat(timespec="seconds")
def digest(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
 return h.hexdigest()
def scan(folder,hash_now=False):
 folder=os.path.abspath(os.path.expanduser(folder))
 if not os.path.isdir(folder): raise ValueError("Choose an existing accessible folder.")
 db=get_db(); start=stamp()
 job=db.execute("INSERT INTO scan_jobs(root_path,started_at,status) VALUES(?,?,?)",(folder,start,"running")).lastrowid
 count=errors=0
 for base,dirs,names in os.walk(folder):
  dirs[:]=[d for d in dirs if d not in SKIP]
  for name in names:
   path=os.path.join(base,name)
   try:
    st=os.stat(path,follow_symlinks=False)
    if not os.path.isfile(path): continue
    ext=os.path.splitext(name)[1].lower(); sha=digest(path) if hash_now else None
    db.execute("""INSERT INTO files(absolute_path,filename,extension,size_bytes,created_at,modified_at,scanned_at,content_hash,hash_checked_at)
    VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(absolute_path) DO UPDATE SET filename=excluded.filename,extension=excluded.extension,size_bytes=excluded.size_bytes,created_at=excluded.created_at,modified_at=excluded.modified_at,scanned_at=excluded.scanned_at,content_hash=COALESCE(excluded.content_hash,files.content_hash),hash_checked_at=COALESCE(excluded.hash_checked_at,files.hash_checked_at)""",
    (path,name,ext,st.st_size,datetime.fromtimestamp(st.st_ctime).astimezone().isoformat(),datetime.fromtimestamp(st.st_mtime).astimezone().isoformat(),stamp(),sha,stamp() if sha else None)); count+=1
   except OSError: errors+=1
 db.execute("UPDATE scan_jobs SET completed_at=?,files_seen=?,status=? WHERE id=?",(stamp(),count,"completed" if not errors else "completed_with_errors",job))
 db.execute("INSERT INTO audit_log(action,details,created_at) VALUES(?,?,?)",("SCAN",f"{folder}; files={count}; errors={errors}",stamp())); db.commit()
 return count,errors
def hash_missing():
 db=get_db(); rows=db.execute("SELECT id,absolute_path FROM files WHERE content_hash IS NULL").fetchall(); n=0
 for r in rows:
  try: db.execute("UPDATE files SET content_hash=?,hash_checked_at=? WHERE id=?",(digest(r["absolute_path"]),stamp(),r["id"])); n+=1
  except OSError: pass
 db.commit(); return n
def dashboard():
 db=get_db(); total=db.execute("SELECT COUNT(*) n,COALESCE(SUM(size_bytes),0) bytes FROM files").fetchone()
 ext=db.execute("SELECT COALESCE(NULLIF(extension,''),'[no extension]') label,COUNT(*) n,SUM(size_bytes) bytes FROM files GROUP BY extension ORDER BY bytes DESC LIMIT 8").fetchall()
 large=db.execute("SELECT filename,absolute_path,size_bytes,modified_at FROM files ORDER BY size_bytes DESC LIMIT 8").fetchall()
 scans=db.execute("SELECT * FROM scan_jobs ORDER BY id DESC LIMIT 5").fetchall()
 dup=db.execute("SELECT COUNT(*) n FROM (SELECT content_hash FROM files WHERE content_hash IS NOT NULL GROUP BY content_hash HAVING COUNT(*)>1)").fetchone()["n"]
 return total,ext,large,scans,dup
def search(q="",ext="",lo="",hi=""):
 sql="SELECT * FROM files WHERE 1=1"; args=[]
 if q: sql+=" AND filename LIKE ?"; args.append("%"+q+"%")
 if ext: sql+=" AND lower(extension)=?"; args.append(ext.lower() if ext.startswith(".") else "."+ext.lower())
 if lo: sql+=" AND size_bytes>=?"; args.append(int(lo))
 if hi: sql+=" AND size_bytes<=?"; args.append(int(hi))
 return get_db().execute(sql+" ORDER BY modified_at DESC LIMIT 500",args).fetchall()
def duplicates():
 hash_missing()
 return get_db().execute("SELECT content_hash,COUNT(*) n,SUM(size_bytes) bytes,GROUP_CONCAT(absolute_path,char(10)) paths FROM files WHERE content_hash IS NOT NULL GROUP BY content_hash HAVING COUNT(*)>1 ORDER BY bytes DESC").fetchall()
def allocation():
 rows=get_db().execute("SELECT size_bytes FROM files").fetchall(); block=4096
 logical=sum(r[0] for r in rows); blocks=sum((r[0]+block-1)//block for r in rows)
 return {"block":block,"files":len(rows),"logical":logical,"blocks":blocks,"allocated":blocks*block,"slack":blocks*block-logical}
