import os, urllib2
import flask, flask.views
import sendgrid

import urllib
from bs4 import BeautifulSoup

import random
import shutil
from PIL import Image

import json

app = flask.Flask(__name__)

# Don't do this!
app.secret_key = "bacon"

def white_pic(filename):
    """
    Paints the picture white
    """
    # Pic location
    pic_location = os.getcwd()+"/static/"+filename
    
    # Open Pic
    picture = Image.open(pic_location)
    
    # Get the size of the image
    width, height = picture.size
    
    # Process every pixel
    for x in range(width):
        for y in range(height):
            current_color = picture.getpixel( (x,y) )
            #print "Old: ",current_color
            ####################################################################
            # Do your logic here and create a new (R,G,B) tuple called new_color
            ####################################################################
            picture.putpixel( (x,y), (255,255,255))
            current_color2 = picture.getpixel( (x,y) )
            #print "new: ", current_color2, "\n"
    
    new_photo_test = pic_location
    picture.save(new_photo_test)

def random_id():
    """
    Creates a random string of numbers of length 20
    """
    numbers = "0123456789"
    
    id = ""
    
    for count in range(20):
        
        id += random.choice(numbers)
        
    print id
    return id

def downloading_pic(url):
    """
    This functions goes to the page of the given url, scrapes it for the
    url of the pic, and then save the pic in the current directory.
    """
    # Create soup
    html    = urllib.urlopen(url)
    content = html.read()
    soup    = BeautifulSoup(content)
    
    # Scrapes for the url of the pic
    url_of_pic = str(soup).split(">")[4].split("<")[0]
    
    # creates a randome file name
    file_name = random_id()+".png"

    # Saves the pic to a file
    f = open(file_name,'wb')
    f.write(urllib.urlopen(url_of_pic).read())
    f.close()
    
    # moving the pic to the static directory
    current_dir = os.getcwd()
    shutil.move(file_name, current_dir+"/static")
    
    # Returns the file name so that I can use it 
    # when I send the file.
    return file_name


class Email(flask.views.MethodView):
    
    def get(self):
        
        return flask.render_template("index.html")
    
    def post(self):
        
        # Getting the info from the form
        from_name = flask.request.form["from_name"]
        from_email = flask.request.form["from_email"]
        message    = flask.request.form["message"]
        to_name    = flask.request.form["to_name"]
        to_email   = flask.request.form["to_email"]
        
        # Stores the info
        info = [from_name, from_email, message, to_name, to_email]
        
        # Insert magicmail code
        url = "http://api.img4me.com/?text="+str(message)+"&font=arial&fcolor=000000&size=10&bcolor=FFFFFF&type=png"
        
        pic_file_name = downloading_pic(url)
       
        html_body = "<img src=http://33c0ffc2.ngrok.com/static/"+pic_file_name+">"
        
        
        # TESTING: Sendgrid regular email
        # Connects to sendgrid
        s = sendgrid.Sendgrid("crazcalm", "11Crazcalm", secure=True)
        
        message = sendgrid.Message(from_email, "Your target", message, html_body)
        message.add_to(to_email, to_name)
        
        message.add_unique_argument("filename",pic_file_name)
        
        s.web.send(message)
        
        flask.flash(info)
        
        #print flask.request.form
        
        
        return self.get()
    

@app.route("/hook", methods=["POST", "GET"])
def hook():
    print flask.request
    print flask.request.data
    
    hack = flask.request.data
    
    print str(hack)
    print hack.split(":"),"\n\n"
    print hack.split(":")[3]
    print hack.split(":")[3].split(",")[0]
    
    pic_file_name = hack.split(":")[3].split(",")[0][1:-1]
    white_pic(pic_file_name)

    
    return "Hello Hook!"
   
        
        
        
app.add_url_rule('/', view_func=Email.as_view('main'), methods=['GET', 'POST'])


app.debug = True
app.run()
