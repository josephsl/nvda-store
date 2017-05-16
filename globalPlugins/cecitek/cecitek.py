# *-* coding: utf8 *-*

import requests
import json
import logHandler

class Cecitek(object):
    URL = 'https://www.cecitek.fr/'
    notifications = []

    def __init__(self):
        super(Cecitek, self).__init__()
        self.session = requests.Session()
        
    def ping(self):
        resp = self.query()
        return resp.status == 200


    def query(self, *args, **kwargs):
        kwargs['_viewType'] = 'json';
        if 'module' not in kwargs:
            kwargs['module'] = 'index'
        try:
            resp = self.session.post(self.URL, data=kwargs, verify=False)
        except Exception, e:
            logHandler.log.error("Failed to send request to the server: %s" % e)
            return None
        if resp.status_code == 200:
            if '_binary' in kwargs and kwargs['_binary'] is True:
              return resp.content
            try:
              data = json.loads(resp.text)
            except:
              logHandler.log.info("Invalid response from the server: %s" %(resp.text))
              return False                
            if len(data[u'moduleNotifications']) > 0:
              for n in data[u'moduleNotifications']:
                self.notifications.append(notif)
        if 'module' in kwargs:
          module = kwargs['module']
          func = getattr(self, "on_%s" % module, None)
          print "calling on_%s" % module
          if func:
            return func(kwargs, data)
          else:
            return False

    def authenticate(self, username, password):
        resp = self.query(module='index', action='login', username=username, passwd=password)

    def on_login(self, params, data):
        self.authenticated = data[u'authenticated']

    def on_index(self, params, data):
        if 'action' in params and params['action'] == 'login':
            return self.on_login(params, data)
        return True

    def on_episode(self, params, data):
        return data[u'episodes'];

    def on_nvda(self, params, data):
        modules = data[u'modules']
        return modules

    def getNvdaModules(self):
        return self.query(module='nvda', action='index')
    def getAddonFile(self, id, id_addon):
      res = self.query(module='nvda', action='download', id=id, id_version=id_addon, _binary=True)
      logHandler.log.info("Downloaded %d bytes from the server" %(len(res)))
      return res
    def getNotifications(self):
        notifs = self.notifications
        self.notifications = []
        return notifs

    
    def getEpisodes(self, limit=10):
        return self.query(module='episode', action='list', limit=limit)

    def cmd_detail(self, args):
        id = args[0]
        self.query(module='episode', action='view', id=id)

    def cmd_comment(self, args):
        id = args[0]
        self.query(module='episode', action='comment', epId=id)
    
