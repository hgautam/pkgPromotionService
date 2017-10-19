#!/usr/bin/python

import cgi, cgitb, json, sys, os
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

def checkStatus():
        # Create instance of FieldStorage
        form = cgi.FieldStorage()

        # Get data from fields
        package_name = str(form.getvalue('package_name'))
        logger.debug('package name is '+ package_name)

        promotedPath = '/cronus/promotionData/status/'
        promotedPkg = package_name + '.promoted'
        pkgAbsPath = promotedPath + promotedPkg
        logger.debug('abs path ' + pkgAbsPath)
        if os.path.exists(pkgAbsPath):
           logger.info(package_name + ' is successfully promoted')
           outputJSON('Successfully promoted', 200)
        else:
           logger.info('Not promoted')
           outputJSON('Not promoted', 404)

if __name__ == "__main__":
    LOG_FILENAME = '/var/tmp/promotionStatus.log'
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
    checkStatus()
