import os,tempfile,unittest
from app import create_app
class WebTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory(); self.app=create_app({"TESTING":True,"DATABASE":os.path.join(self.t.name,"db.sqlite")}); self.c=self.app.test_client()
 def tearDown(self): self.t.cleanup()
 def test_home_health(self):
  self.assertEqual(self.c.get("/").status_code,200); self.assertEqual(self.c.get("/health").json["status"],"ok")
 def test_scan_search(self):
  d=os.path.join(self.t.name,"sample"); os.mkdir(d)
  with open(os.path.join(d,"alpha.txt"),"w") as f:f.write("test data")
  self.c.post("/scan",data={"folder":d})
  self.assertIn(b"alpha.txt",self.c.get("/files?q=alpha").data)
 def test_storage(self): self.assertEqual(self.c.get("/storage").status_code,200)
if __name__=="__main__": unittest.main()
