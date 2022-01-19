from flask import *
from flask import render_template
import re
import os
import json
import requests
from urllib.parse import urlparse

configFile = open("config.json")
config = json.loads(configFile.read())
print(config["Regions"])
configFile.close()

COUNTRY = config["Regions"]

HOME = config["URL"]

HOME_BUTTON = "<div style=\"z-index: 0\"><a href=\"/?new_site=1\" target=\"_self\"><input type=\"button\", value=\"CLOSE\" style=\"position: absolute; color:white; font-size:35px; background-color:darkcyan; cursor: pointer; top:0; z-index:-10; left: 0; htight: 75px\"></a></div><p style=\"font-size:25px;position: absolute;  top:0; z-index:-10; right: 0\">site: "
HOME_BUTTON_TOP = "<div style=\"z-index: 0\"><a href=\"/?new_site=1\" target=\"_self\"><input type=\"button\", value=\"CLOSE\" style=\"position: auto; color:white; font-size:35px; background-color:darkcyan; cursor: pointer; top:0; z-index:-10; left: 0; htight: 75px\"></a></div><p style=\"font-size:25px;position: absolute;  top:0; z-index:-10; right: 0\">site: "

ips = {}

HOSTNAME = "localhost"

app = Flask(__name__)
app.secret_key = os.getenv("secretKey")




@app.route("/<path:path>", methods=["GET", "POST"])
@app.route("/", defaults={"path":""}, methods=["GET", "POST"])
def main(path):
    return "Being changed to work with github"
    if "X-Forwarded-For" in request.headers:
      ipResponse = requests.get("https://ipinfo.io/" + request.headers["X-Forwarded-For"] + "/json", verify=True)
    else:
      ipResponse = requests.get("https://ipinfo.io/" + request.remote_addr + "/json", verify=True)
    ipJson = ipResponse.json()
    if ipJson["country"] not in  COUNTRY:
      return render_template("wrongRegion.html", r=ipJson["country"])
    
    if path == "favicon.ico":
      print("icon")
      return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    #return "disabled"
    if request.remote_addr not in list(ips.keys()):
      if request.method == "GET":
        return render_template("index.html", error=0, home=HOME)
      else:
        print(request.form['URL'], requests.head(request.form['URL']).status_code)
        if requests.head(request.form['URL']).status_code == 200 or requests.head(request.form['URL']).status_code == 301 or requests.head(request.form['URL']).status_code == 302:
          ips[request.remote_addr] = request.form['URL']
          print('success')
        else:
          print('fail')
          return render_template("index.html", error=1, home=HOME)


    #print(">", request.remote_addr, "<")
    redirectVal = ""
    if "new_site" in request.args:
      if request.remote_addr in list(ips.keys()):
        
        if request.args.get("new_site") == "1":
          ips.pop(request.remote_addr)
        else:
            try:
              if requests.head(request.args.get("new_site")).status_code == 200 or requests.head(request.args.get("new_site")).status_code == 301 or requests.head(request.args.get("new_site")).status_code == 302:
                site = urlparse(request.args.get("new_site"))
                print(site.scheme + "://" + site.netloc)
                ips[request.remote_addr] = site.scheme + "://" + site.netloc
                
                redirectVal = site.path
              else:

                ips.pop(request.remote_addr)
            except:
              ips.pop(request.remote_addr)
      if redirectVal != "":
        return redirect(redirectVal)
      else:
        return redirect("/")
    if request.remote_addr in list(ips.keys()):
        #try:
        path = request.full_path
        ##print(ips, ips[request.remote_addr])
        url = ips[request.remote_addr] + path
        if url[-1] == "?":
            url = url[:-1]
        if url[-1].lower() == "s" and url[-2].lower() == "j" and url[-3] == ".":
            print("JAVASCRIPT DETECTED") 
            
        #print("URL:", url, "path:", path)
        #print(request.method)
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
          print("EDITING...")
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
            output_string = output_string_0[0] +  "<body" + output_string_1[0] + ">" + HOME_BUTTON_TOP + ips[request.remote_addr] + output_string_1[1]
          elif "</html>" in output_string:
            output_string_0 = output_string.split("</html>")
            output_string = output_string + HOME_BUTTON + ips[request.remote_addr] + "</html>"
          else:
            output_string += HOME_BUTTON + ips[request.remote_addr]

          page = output_string


          ##print("ERROR: unable to get page")
          #page = render_template("404Error.html")
        ##print(" --- page: " + page)
        #print(ips[request.remote_addr])

        return page
        #except:
        #    #print("error: resource not found")
        #    return render_template("404Error.html", page=request.full_path)
    else:
      #print(" --- 404: not found ---")
      url = path
      return render_template("404Error.html", page=url)
#@app.route("/NEW_SITE")
#def newsite():
#  if request.remote_addr in list(ips.keys()):
#    ips.pop(request.remote_addr)
#  return redirect("/")
#@app.route("/USEFUL_LINKS")
#def newsite():
#  if request.remote_addr in list(ips.keys()):
#    ips.pop(request.remote_addr)
#  return redirect("/")

      

if __name__ == '__main__':
    app.run(port=80, host="0.0.0.0", debug=True)
