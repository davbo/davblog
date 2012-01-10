"""
A basic blog interface for Vim.
Supports basic CRUD functions

Basic UI classes are from Michael Brown's excellent VimTrac Plugin:
http://www.vim.org/scripts/script.php?script_id=2147
"""
import vim, urllib, urllib2, json, webbrowser, base64

########################
# User Interface Base Classes 
########################
class VimWindow:
    """ wrapper class of window of vim """
    def __init__(self, name = 'WINDOW'):
        """ initialize """
        self.name       = name
        self.buffer     = None
        self.firstwrite = 1
        self.winnr      = 0
    def isprepared(self):
        """ check window is OK """
        if self.buffer == None or len(dir(self.buffer)) == 0 or self.getwinnr() == -1:
          return 0
        return 1
    def prepare(self):
        """ check window is OK, if not then create """
        if not self.isprepared():
          self.create()
    def on_create(self):
        """ On Create is used  by the VimWindow subclasses to define vim
            mappings and buffer settings
        """
        pass
    def getwinnr(self):
        """ Returns the vim window number for wincmd calls """
        return int(vim.eval("bufwinnr('"+self.name+"')"))
    def write(self, msg):
        """ write to a vim buffer """
        self.prepare()
        self.on_before_write()
        if self.firstwrite == 1:
          self.firstwrite = 0

          #TODO tickets #7 and #56 setting to utf-8 causes sporadic ticket Encoding errors
          msg = msg.encode('utf-8', 'ignore')
          #msg = msg.encode('ascii', 'ignore')

          self.buffer[:] = str(msg).split('\n')
        else:
          self.buffer.append(str(msg).split('\n'))
        self.command('normal gg')
        self.on_write()
    def on_before_write(self):
        pass
    def on_write(self):
        ''' for vim commands after a write is made to a buffer '''
        pass
    def dump (self):
        """ returns the contents buffer as a string """
        return "\n".join (self.buffer[:])
    def create(self, method = 'new'):
        """ creates a  window """
        vim.command('silent ' + method + ' ' + self.name)
        vim.command("setlocal buftype=nofile")
        self.buffer = vim.current.buffer

        self.width  = int( vim.eval("winwidth(0)")  )
        self.height = int( vim.eval("winheight(0)") )
        self.winnr = self.getwinnr()
        self.on_create()
    def destroy(self):
        """ destroy window """
        if self.buffer == None or len(dir(self.buffer)) == 0:
          return
        #if self.name == 'LOG___WINDOW':
        #  self.command('hide')
        #else:
        self.command('bdelete ' + self.name)
        self.firstwrite = 1
    def clean(self):
        """ clean all datas in buffer """
        self.prepare()
        self.buffer[:] = []
        self.firstwrite = 1
    def command(self, cmd):
        """ go to my window & execute command """
        self.prepare()
        winnr = self.getwinnr()
        if winnr != int(vim.eval("winnr()")):
          vim.command(str(winnr) + 'wincmd w')
        vim.command(cmd)
    def set_focus(self):
        """ Set focus on the current window """
        vim.command( str(self.winnr) + ' wincmd w')
    def resize_width(self, size = False):
        """ resizes to default width or specified size """
        self.set_focus()
        if size  == False:
            size = self.width
        vim.command('vertical resize ' + str(size))
class NonEditableWindow(VimWindow):
    def on_before_write(self):
        vim.command("setlocal modifiable")
    def on_write(self):
        vim.command("setlocal nomodifiable")
    def clean(self):
        """ clean all datas in buffer """
        self.prepare()
        vim.command('setlocal modifiable')
        self.buffer[:] = []
        self.firstwrite = 1
class UI:
    """ User Interface Base Class """
    def __init__(self):
        """ Initialize the User Interface """
    def open(self):
        """ change mode to a vim window view """
        self.create()
    def normal_mode(self):
        """ restore mode to normal """
        if self.mode == 0: # is normal mode ?
            return


        # destory all created windows
        self.destroy()

        #self.winbuf.clear()
        self.file    = None
        self.line    = None
        self.mode    = 0
        self.cursign = None


class BlogUI(UI):
    def __init__(self):
        self.postwindow = PostWindow()
        self.tocwindow = TOCWindow()

    def create(self):
        vim.command('tabnew')
        self.postwindow.create(' 30 vnew')
        vim.command ("only")
        self.tocwindow.create("vertical aboveleft new")
        return False

    def destroy(self):
        self.postwindow.destroy()
        self.tocwindow.destroy()


class TOCWindow (NonEditableWindow):
    """ Blog Post Table Of Contents """
    def __init__(self, name = 'POSTS_TOC'):
        VimWindow.__init__(self, name)

    def on_create(self):
        vim.command('nnoremap <buffer> <cr> :python davblog.post_view("CURRENTLINE")<cr>')
        vim.command('nnoremap <buffer> dd :python davblog.delete_post("CURRENTLINE")<cr>')
        vim.command('setlocal winwidth=30')
        vim.command('vertical resize 30')
        vim.command('setlocal cursorline')
        vim.command('setlocal linebreak')
        vim.command('setlocal noswapfile')

    def on_write(self):
        NonEditableWindow.on_write(self) 

class PostWindow(VimWindow):
    def __init__(self, name='POST_WINDOW'):
        VimWindow.__init__(self, name)
    def on_create(self):
        vim.command('setlocal syntax=markdown')
        vim.command('nnoremap <buffer> <leader>p :python davblog.davblog_post()<cr>')

class Davblog:
    def __init__(self): 
        self.blog_url = 'http://davbo.org'

        self.uiblog = BlogUI()

    def delete_post(self, title=None):
        if title == 'CURRENTLINE':
            title = vim.current.line
        else:
            return False
        titles = self.get_titles()
        slug = titles[title]
        confirm = python_input('Are you sure you want to delete this post?')
        if confirm.lower() == 'yes' or confirm.lower() == 'y':
            response = urllib.urlopen(self.blog_url+"/api/delete_post/"+slug)
            self.uiblog.destroy()
            self.davblog_browse()


    def post_view(self, title=None):
        if title == 'CURRENTLINE':
            title = vim.current.line
        if title == 'new':
            self.uiblog.postwindow.write(python_input("Enter post title: "))
            self.uiblog.postwindow.write('')
            return
        titles = self.get_titles()
        slug = titles[title]
        response = urllib.urlopen(self.blog_url+"/api/get_post/"+slug)
        self.uiblog.postwindow.clean()
        self.uiblog.postwindow.write(title)
        self.uiblog.postwindow.write('')
        for line in eval(response.read()).splitlines():
            self.uiblog.postwindow.write(line)

    def davblog_post(self):
        current_buffer = vim.current.buffer
        data = {'title': current_buffer[0],
                'text': "\n".join(current_buffer[2:])}
        data = {'post': json.dumps(data)}
        username = python_input('Username')
        password = python_input('Password')
        request = urllib2.Request(self.blog_url+"/api/make_post", urllib.urlencode(data))
        base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)   
        response = json.loads(urllib2.urlopen(request).read())
        if 'error' in response:
            confirm = python_input('Are you sure you want to edit this post?')
            if confirm.lower() == 'yes' or confirm.lower() == 'y':
                data['confirm'] = True
                request = urllib2.Request(self.blog_url+"/api/make_post", urllib.urlencode(data))
                request.add_header("Authorization", "Basic %s" % base64string)   
                response = json.loads(urllib2.urlopen(request).read())
        if 'success' in response:
            webbrowser.open(self.blog_url+response['success'])

    def get_titles(self):
        response = urllib.urlopen(self.blog_url+"/api/get_titles")
        return json.loads(response.read())

    def davblog_browse(self):
        self.uiblog.open()
        titles = self.get_titles()
        for title, slug in titles.items():
            self.uiblog.tocwindow.write(str(title))
        self.uiblog.tocwindow.write('')
        self.uiblog.tocwindow.write('----')
        self.uiblog.tocwindow.write('')
        self.uiblog.tocwindow.write('new')


def python_input(message = 'input'):
  vim.command('call inputsave()')
  vim.command("let user_input = input('" + message + ": ')")
  vim.command('call inputrestore()')
  return vim.eval('user_input')

def davblog_init():
    global davblog
    davblog = Davblog()
