import sublime, sublime_plugin
from urllib.request import urlopen
import http.cookiejar, urllib.request
from urllib.request import Request
import json
import http

class botprintCommand(sublime_plugin.TextCommand):
	def run(self,edit,**response_json):
		msg = response_json.get('error_message','Bot is valid')
		sublime.status_message(msg)
		self.view.insert(edit,self.view.size(),msg)

class ValidateBotCommand(sublime_plugin.TextCommand):

	def get_settings(self):
		self.settings =	sublime.load_settings("Preferences.sublime-settings").get('divvycloud')
		self.username = self.settings.get('username')
		self.password = self.settings.get('password')
		self.hostname = self.settings.get('hostname')
		self.port = self.settings.get('port')

	def create_connection(self):
		self.headers = {'Content-Type': 'application/json;charset=UTF-8',"Accept-Encoding":"gzip, deflate"}
		self.conn = http.client.HTTPConnection(self.hostname,self.port)
		return

	def auth(self):
		auth_data = {
			  "user_email": "brian@divvycloud.com",
			  "user_password": "killer23"
		}
		auth_data = json.dumps(auth_data).encode('utf8')
		self.conn.request("POST","/v2/public/user/login",auth_data,headers=self.headers)
		response = self.conn.getresponse()

		if(response.status != 200):
			self.out_panel.run_command('botprint',{
				"error_message" : "Unable to authenticate with DivvyCloud"
				})
			return

		response_data = json.loads(response.read().decode('utf8'))
		session_id = response_data['session_id']
		self.headers.update({"X-Auth-Token":session_id})

	def validate_bot(self,content_data):

		self.conn.request('POST','/plugin/botfactory/validate?format=yaml',content_data,self.headers)
		response = self.conn.getresponse()
		response_data = response.read().decode('utf8')
		response_json = json.loads(response_data)
		self.out_panel = self.view.window().create_output_panel('Test')
		self.view.window().run_command('show_panel',{"panel":"output.Test"})
		self.out_panel.run_command('botprint',response_json)


	def run(self, edit):
		self.get_settings()
		self.create_connection()
		self.auth()

		# # Get the contents of this file
		contents = self.view.substr(sublime.Region(0, self.view.size()))
		content_data = contents.encode('ascii')

		self.validate_bot(content_data)

