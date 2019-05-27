# coding = utf-8
import os

from contents.global_setting.set_global import LOCAL_IP
from mall.settings import BASE_DIR

with open("%s/utils/fastdfs/client.conf" % BASE_DIR, "w") as f:
    f.write("""
connect_timeout=30\n
network_timeout=120\n
base_path=%s\n
tracker_server=%s:22122\n
log_level=info\n
use_connection_pool = false\n
connection_pool_max_idle_time = 3600\n
load_fdfs_parameters_from_tracker=false\n
use_storage_id = false\n
storage_ids_filename = storage_ids.conf\n
http.tracker_server_port=80
    """ % (BASE_DIR, LOCAL_IP))

# 删除docker, storage
os.system("docker container stop tracker")
os.system("docker container stop storage")
os.system("docker container rm tracker")
os.system("docker container rm storage")

# 创建docker
os.system("docker run -dti --network=host --name tracker -v"
          " /var/fdfs/tracker:/var/fdfs delron/fastdfs tracker")
os.system("docker run -dti --network=host --name storage -e TRACKER_SERVER=%s:22122 "
          "-v /var/fdfs/storage:/var/fdfs delron/fastdfs storage" % LOCAL_IP)
