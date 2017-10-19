#!/usr/bin/python
import time, atexit, os, fnmatch, shutil
import requests, logging, logging.handlers
from requests_toolbelt.multipart.encoder import MultipartEncoder
def exit_handler():
    logger.info('The process is ending...')
atexit.register(exit_handler)

def postFile(pkgs):
   if len(pkgs) < 1:
      return 1
   remoteStatus = {}
   rtnCode = -1
   for pkg in pkgs:
      pkgPath = pkg.split(':')
      srcPath = pkgPath[0]
      tgtPath = pkgPath[1]
      logger.debug(srcPath)
      logger.debug(tgtPath)
      status = multiPartUpload(srcPath, tgtPath)
      remoteStatus[srcPath] = status

   statusList = remoteStatus.values()
   logger.debug(statusList)
   for returnCode in statusList:
       if returnCode == 200 or returnCode == 403:
          rtnCode = 0
       else:
          rtnCode = 1

   return rtnCode

def multiPartUpload(srcPath, tgtPath):
    return 200
    URL = 'http://cronus-srepo.vip.ebay.com/cgi-bin/saveFile.py'
    m = MultipartEncoder(
          fields = {'file': (tgtPath, open(srcPath, 'rb'), 'text/plain')}
    )
    r = ''
    try:
       r = requests.post(URL, data=m,
                  headers={'Content-Type': m.content_type})
    #print(r.text)
    #logger.debug(print(r.text))
    except requests.exceptions.ConnectionError as e:
       logger.error('Connection error', exc_info=True)

    # pasrse the string
    #print(r.text)
    logger.info(r.text)
    list = r.text.strip('\n').split(':')
    str = list[2].rstrip('\n\t')[:-1]
    logger.debug(int(str))
    return int(str)

def start():
  while True:
    logger.info('post handler starting a new run..')
    JOB_QUEUE_DIR = ('/cronus/promotionData/queue')
    JOB_STATUS_DIR = '/cronus/promotionData/status'
    result = []
    for root, dirs, files in os.walk(JOB_QUEUE_DIR):
       for name in files:
          if fnmatch.fnmatch(name, '*.queued'):
             logger.debug('name is ' + name)
             logger.debug('root is ' + root)
             logger.debug(name.split('.')[0])
             modName = name.split('.')[0] + '.inprocess'
             logger.debug('modfied name is ' + modName)
             shutil.move(os.path.join(root, name), os.path.join(root, modName))
             result.append(os.path.join(root, modName))
    logger.debug('result is: '.join(result))
    if len(result) < 1:
       logger.info('Nothing queued')
    #iterate over the list
    for file in result:
       logger.debug('file in result ' + file)
       if os.path.exists(file):
          with open(file, 'r') as f:
             data = ''
             try:
                data = f.read()
             except : # whatever reader errors you care about
                logger.error('cant read the file', exc_info=True)
             #print('print 3 ' + data)
             modData = data.strip('\n')
             pkgs = modData.split(';')
             pkgName = pkgs.pop(0)
             logger.debug('pkgName is ' +  pkgName)
             #logger.debug('pks list is: '.join( pkgs))
             logger.debug(pkgs)
             status =  postFile(pkgs)
             #status = 1
             if(status == 0):
                shutil.move(JOB_QUEUE_DIR + '/' + pkgName + '.inprocess', JOB_QUEUE_DIR + '/' + pkgName + '.promoted')
                logger.info(pkgName + ' is successfully promoted')

    logger.info('Going to sleep...')
    time.sleep(5)

if __name__ == "__main__":
    LOG_FILENAME = '/var/tmp/postHandler.log'
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # create a file handler
    #handler = logging.FileHandler('postHandler.log')
    handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=5000000, backupCount=3)
    handler.setLevel(logging.DEBUG)

    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(handler)
    start()
