import json
import logging
import subprocess


def run(image, a_id, domain, paths=None):
    # TODO: Run docker image/kubernetes POD creation
    res = ""
    if not paths is None:
        res = json.dumps(paths)

    subprocess.Popen(["docker", "run", "-v", "/tmp/data:/data", "--net=host", "-e",
                      "DOMAIN=%s" % domain, "-e", "ANALYZER=%s" % a_id, "-e", "SCANS=%s" % res,
                      image])
    logging.info('docker run -v /tmp/data:/data --net=host -e DOMAIN="%s" -e ANALYZER="%s"  -e SCANS="%s" %s' % (domain, a_id, res.replace('"','\\"'), image))
