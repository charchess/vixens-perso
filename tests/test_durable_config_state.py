import unittest
from pathlib import Path
ROOT=Path(__file__).parents[1]
STATEFUL=("amule","bookshelf","lidarr","mylar","prowlarr","pyload","qbittorrent","radarr","sabnzbd","sonarr","whisparr","homepage")
class DurableConfigState(unittest.TestCase):
 def test_inventory_declares_all_owners_and_migration_safety(self):
  doc=(ROOT/"docs/stateful-config-ownership.md").read_text()
  for app in STATEFUL:self.assertIn(app,doc)
  for term in ("snapshot","copy","verification","cutover","rollback"):self.assertIn(term,doc)
 def test_stateful_config_mounts_use_declared_pvcs(self):
  for app in STATEFUL:
   base=ROOT/("apps/70-tools/homepage/base" if app=="homepage" else f"apps/20-media/{app}/base")
   self.assertIn("pvc.yaml",(base/"kustomization.yaml").read_text())
   self.assertIn("persistentVolumeClaim",(base/"deployment.yaml").read_text())
   self.assertTrue((base/"pvc.yaml").is_file())
if __name__=="__main__":unittest.main()
