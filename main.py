from flask import *
from flask import render_template
import os
global CURRENTNUM
CURRENTNUM = 0



from gevent.pywsgi import WSGIServer
import json
import requests
from urllib.parse import urlparse

configFile = open("config.json")
config = json.loads(configFile.read())
print("--- Configuration ---")
print("\033[94m", end="")
print("Version: " + config["Version"])
print("Regions: " + str(config["Regions"]))
print("Default URL: " + config["URL"])
print("fg: " + config["fg"])
print("bg: " + config["bg"])
print("\033[93m", end="")
print("Known URLs to fail: ")
for i in config["KnownURLs"]:
  print(i)
print("\033[0m", end="")
print("--- Server output ---")

configFile.close()

#parameters changeable by config.json, check documentation on github
COUNTRY = config["Regions"]
DEBUG_MODE=False
HOME = config["URL"]
BG = config["bg"]
FG = config["fg"]

HOME_BUTTON = "<div style=\"z-index: 0\"><a href=\"/?new_site=1\" target=\"_self\"><input type=\"button\", value=\"CLOSE\" style=\"position: absolute; color:white; font-size:35px; background-color:darkcyan; cursor: pointer; top:0; z-index:-10; left: 0; htight: 75px\"></a></div><p style=\"font-size:25px;position: absolute;  top:0; z-index:-10; right: 0\">site: "
HOME_BUTTON_TOP = "<div style=\"z-index: 0\"><a href=\"/?new_site=1\" target=\"_self\"><input type=\"button\", value=\"CLOSE\" style=\"position: auto; color:white; font-size:35px; background-color:darkcyan; cursor: pointer; top:0; z-index:-10; left: 0; htight: 75px\"></a></div><p style=\"font-size:25px;position: absolute;  top:0; z-index:-10; right: 0\">site: "

ips = {}
ipsCache = {}

HOSTNAME = "localhost"

app = Flask(__name__)
app.secret_key = os.getenv("secretKey")


def returnVal(val):
  return val

@app.route("/<path:path>", methods=["GET", "POST"])
@app.route("/", defaults={"path":""}, methods=["GET", "POST"])
def main(path):
    NeedsToSetID = ""
    #return "Being changed to work with github"
    X_forward = False
    if "X-Forwarded-For" in request.headers:
      X_forward= True
    if X_forward:
      IP = request.headers["X-Forwarded-For"]
    else:
      IP = request.remote_addr
    if IP in ipsCache.keys():
      if ipsCache[IP] not in COUNTRY:
        return render_template("wrongRegion.html", r=ipJson["country_name"], fg=FG, bg=BG)
    else:
      if X_forward:
        ipResponse = requests.get("https://geolocation-db.com/json/" + request.headers["X-Forwarded-For"] + "", verify=True)
        
        

      else:
        ipResponse = requests.get("https://geolocation-db.com/json/" + request.remote_addr + "", verify=True)
        
      try:
        ipJson = ipResponse.json()
      except:
        print("\033[91mUNABLE TO IDENTIFY COUNTRY IN: " + str(ipResponse) + "\nThis may be due to a request limit\033[0m")
        ipJson = {}
      if "country_code" not in ipJson:
        print(ipJson)
        print("\033[91mUNABLE TO IDENTIFY COUNTRY IN: " + str(ipJson) + "\nThis may be due to a request limit\033[0m")
        return "ERROR - UNABLE TO IDENTIFY REGION. CONNECTION REFUSED."
        
      if ipJson["country_code"] not in COUNTRY:
        return render_template("wrongRegion.html", r=ipJson["country_name"], regions=COUNTRY, fg=FG, bg=BG)
      ipsCache[IP] = ipJson["country_code"]
    if "VPN_DEVICE_ID_VALUE" in request.cookies:
      IdUnique = request.cookies.get("VPN_DEVICE_ID_VALUE")
      DeviceID = request.cookies.get("VPN_DEVICE_ID_VALUE") + "_" + IP
    else:
      global CURRENTNUM
      IdUnique=CURRENTNUM
      NeedsToSetID = CURRENTNUM
      DeviceID = NeedsToSetID
      CURRENTNUM = CURRENTNUM + 1

    
    if path == "favicon.ico":
      return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    if DeviceID not in list(ips.keys()):
      if request.method == "GET":
        return render_template("index.html", error=0, home=HOME, KnownURLs=config["KnownURLs"], version=config["Version"], debug=DEBUG_MODE, fg=FG, bg=BG)
      else:
        try:
          if requests.head(request.form['URL']).status_code == 200 or requests.head(request.form['URL']).status_code == 301 or requests.head(request.form['URL']).status_code == 302:
            ips[DeviceID] = request.form['URL']
            print("\033[92mNew User: total active IPs: " + str(len(ips)) + "\033[0m")
          else:
            return render_template("index.html", error=1, home=HOME, KnownURLs=config["KnownURLs"], version=config["Version"], debug=DEBUG_MODE, fg=FG, bg=BG)
        except:
          return render_template("index.html", error=1, home=HOME, KnownURLs=config["KnownURLs"], version=config["Version"], debug=DEBUG_MODE, fg=FG, bg=BG)


    redirectVal = ""
    if "new_site" in request.args:
      if DeviceID in list(ips.keys()):
        
        if request.args.get("new_site") == "1":
          ips.pop(DeviceID)
        else:
            try:
              if requests.head(request.args.get("new_site")).status_code == 200 or requests.head(request.args.get("new_site")).status_code == 301 or requests.head(request.args.get("new_site")).status_code == 302:
                site = urlparse(request.args.get("new_site"))
                ips[DeviceID] = site.scheme + "://" + site.netloc
                
                redirectVal = site.path
              else:

                ips.pop(DeviceID)
            except:
              ips.pop(DeviceID)
      if redirectVal != "":
        return redirect(redirectVal, fg=FG, bg=BG)
      else:
        return redirect("/")
    if DeviceID in list(ips.keys()):
        path = request.full_path
        url = ips[DeviceID] + path
        if url[-1] == "?":
            url = url[:-1]
        """ #Use this if you want to do something with javascript files
        if url[-1].lower() == "s" and url[-2].lower() == "j" and url[-3] == ".":
            print("JAVASCRIPT DETECTED") 
        """
            
        if redirectVal == "":
          redirectVal = "/"
        if url == redirectVal:

          page = requests.get(url, request.method, headers={'Cache-Control': 'no-cache', "Pragma": "no-cache", "user-agent": ""}).content
          page_decoded = requests.get(url, request.method, headers={'Cache-Control': 'no-cache', "Pragma": "no-cache", "user-agent": ""}).text
        else:
          page = requests.get(url, request.method, headers={}).content
          page_decoded = requests.get(url, request.method, headers={}).text

        isStart = True
        if "<!DOCTYPE html>" in page_decoded:
          output_string = ""
          page_decoded_split0 = page_decoded.split("<a href=")

          for string in page_decoded_split0:
            page_decoded_split1 = string.split(">", maxsplit=1)

            #output_string += page_decoded_split1[0]
            if len(page_decoded_split1) > 1:
              textToAdd = ""
              for i in page_decoded_split1[0].split("\""):
                try:
                  if requests.head(i).status_code == 200:
                    textToAdd = "<a href=\"/?new_site=" +i + "\"/>"
                except:
                  textToAdd = textToAdd
              output_string += textToAdd + page_decoded_split1[1]
              
          if "<body" in output_string:
            output_string_0 = output_string.split("<body", maxsplit=1)
            output_string_1 = output_string_0[1].split(">", maxsplit=1)
            output_string = output_string_0[0] +  "<body" + output_string_1[0] + ">" + HOME_BUTTON_TOP + ips[DeviceID] + output_string_1[1]
          elif "</html>" in output_string:
            output_string_0 = output_string.split("</html>")
            output_string = output_string + HOME_BUTTON + ips[DeviceID] + "</html>"
          else:
            output_string += HOME_BUTTON + ips[DeviceID]

          page = output_string
        resp = make_response(page)
        if NeedsToSetID != "":
          resp.set_cookie('VPN_DEVICE_ID_VALUE', value=str(NeedsToSetID))
        return resp

    else:
      url = path
      return render_template("404Error.html", page=url, fg=FG, bg=BG)

      
if DEBUG_MODE == True:
  if __name__ == '__main__':
      app.run(port=80, host="0.0.0.0", debug=True)
else:
    if __name__ == '__main__':
      httpServer = WSGIServer(('', 80), app, log=None)
      httpServer.serve_forever()
