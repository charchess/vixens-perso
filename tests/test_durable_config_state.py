import unittest
from pathlib import Path
ROOT=Path(__file__).parents[1]
WORKLOADS={"sabnzbd":("apps/20-media/sabnzbd/base","sabnzbd-config-pvc"),"radarr":("apps/20-media/radarr/base","radarr-config-pvc"),"sonarr":("apps/20-media/sonarr/base","sonarr-config-pvc"),"prowlarr":("apps/20-media/prowlarr/base","prowlarr-config-pvc"),"birdnet-go":("apps/20-media/birdnet-go/base","birdnet-go-data-pvc")}
class DurableConfigState(unittest.TestCase):
 def test_each_qualified_workload_binds_mount_claim_and_retained_pvc(self):
  for app,(rel,claim) in WORKLOADS.items():
   base=ROOT/rel; deployment=(base/"deployment.yaml").read_text(); pvc=(base/"pvc.yaml").read_text(); k=(base/"kustomization.yaml").read_text()
   self.assertIn("pvc.yaml",k); self.assertIn("claimName: "+claim,deployment); self.assertIn("name: "+claim,pvc); self.assertIn("storageClassName: storage-rwo-retain",pvc); self.assertIn("ReadWriteOnce",pvc); self.assertIn("vixens.io/config-owner: "+app,pvc)
 def test_inventory_is_limited_to_qualified_workloads(self):
  doc=(ROOT/"docs/stateful-config-ownership.md").read_text()
  for app in WORKLOADS:self.assertIn(app,doc)
  for app in ("amule","bookshelf","lidarr","mylar","pyload","qbittorrent","whisparr","homepage"):self.assertNotIn("| "+app+" |",doc)
if __name__=="__main__":unittest.main()
