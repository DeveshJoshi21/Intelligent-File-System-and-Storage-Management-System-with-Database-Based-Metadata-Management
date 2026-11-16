from flask import Blueprint,render_template,request,redirect,url_for,flash,jsonify
from .services import scan,dashboard,search,duplicates,allocation
bp=Blueprint("ui",__name__)
@bp.get("/")
def home():
 total,ext,large,scans,dup=dashboard()
 return render_template("home.html",total=total,ext=ext,large=large,scans=scans,dup=dup)
@bp.post("/scan")
def do_scan():
 try:
  n,e=scan(request.form.get("folder",""),request.form.get("hash_now")=="on")
  flash(f"Scan complete — {n} files indexed; {e} inaccessible entries skipped.","success")
 except (ValueError,OSError) as ex: flash(str(ex),"error")
 return redirect(url_for("ui.home"))
@bp.get("/files")
def files():
 q=request.args.get("q",""); ext=request.args.get("ext",""); lo=request.args.get("min",""); hi=request.args.get("max","")
 return render_template("files.html",rows=search(q,ext,lo,hi),q=q,ext=ext,lo=lo,hi=hi)
@bp.get("/duplicates")
def dup(): return render_template("duplicates.html",groups=duplicates())
@bp.get("/storage")
def storage(): return render_template("storage.html",r=allocation())
@bp.get("/health")
def health(): return jsonify(status="ok",database="connected")
