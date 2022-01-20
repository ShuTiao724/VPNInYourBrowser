# VPNInYourBrowser
A vpn that sits in your browser, accessible via a website

Example setup: https://VPNInBrowser.jaffa42.repl.co

## **Setup**
1. Put the code onto the server of your choice (provided it supports python). Remplit is recommended as I have made a copy already on there (link goes here).

2. Edit the config file to allow your region to use the system. This is here as some countries ban VPNs. You can also change the default link as well as known links that do not work, or leave as default for an automatic list.

3. Turn on the server and enjoy!


## **Options**

***Version***: Version: set this to the curresnt version.
<br/> Type: String
<br/> Default: "0.1.1"


***Region***: Region to allow. This is the 2 letter country code, e.g. GB or US.
<br/> Type: Array
<br/> Default: ["GB", "US"]
<br/> Note: be careful which countries you allow: in some, VPNs are illegal so do research before adding a country


***URL***: Startup url
<br/>Type: String
<br/>Default: "https://bing.co.uk"
<br/>Note: the "https://" or "http://" part of the URL is required.

***KnownURLs***: Array - This is an array containing URLs that do not work with the VPN.
<br/>Type: Array
<br/>Default: ["https://google.co.uk", "https://youtube.co.uk", "https://wikipedia.co.uk"]
<br/>Note: The software **DOES NOT** block these URLs, it justs shows a message on the homne screen.

***fg***: Text colour
<br/>Type: String

***bg***: Background colour
<br/>Type: String


## **Please note**

This is still in development, there may be security issues.

The following packages that are not pre installed to python are:
- Gevent
 <br/> You can install this via ```pip3 install gevent```
