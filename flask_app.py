import os, urllib, random, shutil
import flask, flask.views
import sendgrid, secret
from bs4 import BeautifulSoup
from PIL import Image

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
            
            # colors the (x,y) pixel white
            picture.putpixel( (x,y), (255,255,255))
    
    new_photo_test = pic_location
    picture.save(new_photo_test)

def deleating_file(pic_file_name):
    """
    Deletes the file at is located in the static folder.
    """
    
    current_dir = os.getcwd()
    
    os.chdir(current_dir+"/static")
    
    if os.path.exists(pic_file_name):
        os.remove(pic_file_name)
        
    os.chdir(current_dir)
    print "The deleting file function ran."


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
        message_subject = flask.request.form["message_subject"]
        message    = flask.request.form["message"]
        to_name    = flask.request.form["to_name"]
        to_email   = flask.request.form["to_email"]
        
        # Stores the info
        info = [from_name, from_email,message_subject, message, to_name, to_email]
        
        # Insert magicmail code
        url = "http://api.img4me.com/?text="+str(message)+"&font=arial&fcolor=000000&size=10&bcolor=FFFFFF&type=png"
        
        pic_file_name = downloading_pic(url)
       
        html_body = "<img src=http://33c0ffc2.ngrok.com/static/"+pic_file_name+"/>"
        
        # Connects to sendgrid
        s = sendgrid.Sendgrid(secret.user_name, secret.user_password, secure=True)
        
        message = sendgrid.Message(from_email, message_subject, message, html_body)
        message.add_to(to_email, to_name)
        
        message.add_unique_argument("filename",pic_file_name)
        
        s.web.send(message)
        
        flask.flash(info)
        
        return self.get()
    



@app.route("/hook", methods=["POST"])
def hook():
    
    try:
        hack = flask.request.data
    
        # Parses the data to get the file name
        pic_file_name = hack.split(":")[3].split(",")[0][1:-1]
        
        white_pic(pic_file_name)
        deleating_file(pic_file_name)
        
    except:
        pass
    
    return "Captain Hook!"
        
     
   
        
        
        
app.add_url_rule('/', view_func=Email.as_view('main'), methods=['GET', 'POST'])

if __name__ == '__main__':
    app.debug = True
    app.run()
