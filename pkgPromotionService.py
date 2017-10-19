#!/usr/bin/python

# Import modules for CGI handling
import cgi, cgitb, json, sys, os, fnmatch
import logging, logging.handlers

cgitb.enable()
def outputJSON(description,code=500):
        message = json.dumps({ "returnCode" : code , "description" : description },sort_keys=True)
        print('Status: 200 OK')
        print('Content-Type: application/json')
        print('Content-Length: %d' % (len(message)))
        print('')
        print(message)
        sys.exit(0)

def createPkgMetadata(pkgName):
        pkgDir = '/cronus/apache2/htdocs/packages'
        queueLocation = '/cronus/promotionData/queue'
        absQueuedPath = queueLocation + '/' + pkgName + '.queued'
        absInprocessPath = queueLocation + '/' + pkgName + '.inprocess'
        result = []
        for root, dirs, files in os.walk(pkgDir):
           for name in files:
               if fnmatch.fnmatch(name, pkgName + '.*'):
                   result.append(os.path.join(root, name))

        #print (result)
        logger.debug(result)
        logger.debug(len(result))

        # this assumes there are two files part of the package
        if len(result) != 2:
          logger.info(pkgName +  ' not found')
          outputJSON(pkgName + ' does not exist', 404)

        pkgDict = {}
        for pkg in result:
                  #print(pkg)
                  #pkglocation = pkg
                  pkgDest = pkg.split('/packages')
                  pkgPath = pkgDest[1][1:]
                  logger.debug(pkgPath)
                  pkgDict[pkg] = pkgPath


        lst = list()
        lst.append(pkgName + ';')
        for path in pkgDict:
                  lst.append(path + ':')
                  lst.append(pkgDict.get(path) + ';')

        #print(lst)
        writeStr = ''.join(lst)[:-1]
        logger.debug(writeStr)
        if os.path.exists(absInprocessPath) or os.path.exists(absQueuedPath):
                  #print('This package is already scheduled for promotion')
                  #result = {'Descriotion':'This package is alredy scheduled for promotion','returnCode':202}
                  logger.info('This package is already scheduled for promotion')
                  description = 'This package is alredy scheduled for promotion'
                  outputJSON(description, 202)

                  #sys.exit(0)
        file = open(absQueuedPath, 'w')
        file.write(writeStr)
        file.close()
        #result = {'Descriotion':'Request successfully queued','returnCode':200}
        logger.info('Request successfully queued')
        description = 'Request successfully queued'
        outputJSON(description, 200)


def startPromotion():
        # Create instance of FieldStorage
        form = cgi.FieldStorage()

        # Get data from fields
        package_name = str(form.getvalue('package_name'))
        approver  = str(form.getvalue('approver'))
        colo = str(form.getvalue('colo'))
        # write above data in a log

        # call createPkgMetadata()
        logger.info('pkg name is ' + package_name)
        logger.info('Package name is ' + package_name)
        logger.info('approver name is ' + approver)

        createPkgMetadata(package_name)

if __name__ == "__main__":
    LOG_FILENAME = '/var/tmp/promotionService.log'
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
    startPromotion()
