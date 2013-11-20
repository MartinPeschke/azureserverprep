from fabric.api import run, sudo
from fabric.context_managers import cd
from fabric.contrib import files
from fabric.operations import put, prompt
from operator import methodcaller

from mako.template import Template

SYSTEM_PACKAGES = ["sudo"
                  , "build-essential"
                  , "libjpeg62-dev"
                  , "libxml2-dev"
                  , "libxslt1-dev"
                  , "unzip"
                  , "libpng12-dev"
                  , "libfreetype6-dev"
                  , "libpcre3-dev"
                  , "libpcre3-dev"
                  , "libssl-dev"
                  , "apache2-utils"
                  , "lib32bz2-dev"
                  , "curl"
                  , "libreadline6"
                  , "libreadline6-dev"
                  , "libmhash2"
                  , "libmhash-dev"
                  , "libmcrypt4"
                  , "libtomcrypt-dev"
                  , "libssl-dev"
                  , "libevent-dev"
                  , "git"]

VERSIONS = {
    "PYTHON":"2.7.5"
    , "NGINX":"1.5.6"
    , "MEMCACHED":"1.4.15"
    , "REDIS":"2.6.16"
    , "NODE":"0.10.21"
}

KEYS = [
  "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCj5VP8RzFPkkN+43Wmg0aN9T5XJKmx0+nBdbr+CKE3xukYkm8Hwg8lTaRQQOFWCiYAH7oxf9g0bT/Vp5a7uDok6Eh9ETPlIle0G+iikh3y+faQmuXbfCxj1Mielgf2Q/tHR6YsS50wfvyBE+hvMWtw54LY/BfoSTkZx5hWF40UcSKA7FvZwC0zbTvyrCczpliPdogazHzTNkmNu2v8QQvxRjg50RNHJI4ECKWUn/WjQUmgJOcnNKisHsK3RdI2joXhrLg86K1ndT2k7shGb7uNElEY0g0/BnEA9tVwJq5dHclJiU72ocuVbC/p4HE1R+DZxiazZhYSJ363yhgLjocL www-data@bellerophon"
]


def set_wwwuser():
    sudo("mkdir /home/www-data")
    sudo("chown www-data: /home/www-data")
    sudo("usermod -d /home/www-data -s /bin/bash www-data")
    with cd("/server"):
      sudo("chown -R www-data: www")
    with cd("/home/www-data"):
      sudo("mkdir .ssh", user = 'www-data')
      sudo("ssh-keygen -t rsa -b 4096", user = 'www-data')
      sudo("cp .ssh/id_rsa.pub .ssh/authorized_keys", user = 'www-data')
    files.append("/home/www-data/.ssh/authorized_keys","\n".join(KEYS), use_sudo=True)

def update():
    sudo("mkdir /server/{src,www} -p")
    sudo("apt-get update")
    sudo("apt-get install -y {}".format(" ".join(SYSTEM_PACKAGES)))


def add_python():
    with cd("/server/src"):
        sudo("wget http://www.python.org/ftp/python/{0}/Python-{0}.tar.bz2".format(VERSIONS['PYTHON']))
        sudo("tar xfvj Python-{}.tar.bz2".format(VERSIONS['PYTHON']))
    with cd("/server/src/Python-{}".format(VERSIONS['PYTHON'])):
        sudo("./configure && make && make install")
        sudo("wget http://peak.telecommunity.com/dist/ez_setup.py")
        sudo("python ez_setup.py")
        sudo("easy_install virtualenv Cython ctypes")


def set_nginx_startup():
    files.upload_template("nginx.initd.tmpl", "/etc/init.d/nginx", {'NGINX_VERSION': VERSIONS['NGINX']}, use_sudo=True)
    sudo("chmod +x /etc/init.d/nginx")
    sudo("update-rc.d nginx defaults")

def set_nginx_conf():
    sudo("mkdir -p /server/nginx/etc/{sites.enabled,sites.disabled}")
    files.upload_template("nginx.conf.tmpl", "/server/nginx/etc/nginx.conf", VERSIONS, use_sudo=True)
    sudo("/etc/init.d/nginx reload")
    
def add_nginx():
    with cd("/server/src"):
        sudo("wget http://nginx.org/download/nginx-{}.tar.gz".format(VERSIONS['NGINX']))
        sudo("tar xfv nginx-{}.tar.gz".format(VERSIONS['NGINX']))
    with cd("/server/src/nginx-{}".format(VERSIONS['NGINX'])):
        sudo("./configure \
            --group=www-data\
            --user=www-data\
            --with-http_ssl_module\
            --prefix=/server/nginx/{}\
            --conf-path=/server/nginx/etc/nginx.conf\
            --error-log-path=/server/nginx/logs/error.log\
            --pid-path=/server/nginx/run/nginx.pid\
            --lock-path=/server/nginx/run/nginx.lock\
            --with-http_gzip_static_module && make && make install".format(VERSIONS['NGINX']))
    set_nginx_startup()
    set_nginx_conf()
    
def add_memcached():
  with cd("/server/src"):
    sudo("wget http://memcached.googlecode.com/files/memcached-{}.tar.gz".format(VERSIONS['MEMCACHED']))
    sudo("tar xfv memcached-{}.tar.gz".format(VERSIONS['MEMCACHED']))
  with cd("/server/src/memcached-{}".format(VERSIONS['MEMCACHED'])):
    sudo("./configure --prefix=/server/memcached && make && make install")
  
  
def add_redis():
  files.append("/etc/apt/sources.list",   "\n\n# /etc/apt/sources.list.d/dotdeb.org.list\ndeb http://packages.dotdeb.org squeeze all\ndeb-src http://packages.dotdeb.org squeeze all", use_sudo = True)
  sudo("apt-get update")
  #TODO: Untrusted source breaks creation
  sudo("apt-get install -y {}".format('redis-server'))
    
def add_node():
  with cd("/server/src"):
    sudo("wget http://nodejs.org/dist/v{0}/node-v{0}.tar.gz".format(VERSIONS['NODE']))
    sudo("tar xfv node-v{}.tar.gz".format(VERSIONS['NODE']))
  with cd("/server/src/node-v{}".format(VERSIONS['NODE'])):
    sudo("./configure && make && make install")
  with cd("/home/www-data"):
	#TODO: It tries executing in home/azureuser and breaks
    sudo("npm install less", user = 'www-data')
    
def add_init_script(name):
  cfg_template = Template(filename='super.initscript.mako')
  files.put("/etc/init.d/super_{}".format(name), cfg_template.render(name = name), escape=False)
  sudo("chmod +x /etc/init.de/super_{}".format(name))
  sudo("update-rc.d super_{} defaults".format(name))
    
def add_nginx_domain_config():
	domain = prompt("What domain you want to run this on?")
	env = prompt("What environment is this? ( live )") or 'live'
	projectname = prompt("What is your package name?")
	port = prompt("Which ports are your servers running on? (comma separated: 6543, 6544, 6545)")
	ports = map(methodcaller("strip"), port.split(","))
	
	cfg_template = Template(filename='nginx.site.conf.tmpl')
	config = cfg_template.render(domain = domain, 
						env=env,
						ports=ports,
						projectname=projectname
						)
	path = '/server/nginx/etc/sites.enabled/{}.{}.conf'.format(projectname,env)
	
	print 'This is the configuration:'.center(80, '-')
	print config
	print '-'*80
	
	confirm = prompt("Upload this file to ({}) ? (y/N)".format(path))
	if confirm == 'Y':
		files.put(path, config, escape=False, use_sudo = True)

	confirm = prompt("Reload nginx? (y/N)")
	if confirm == 'Y':
		sudo("/etc/init.d/nginx reload")
	
	
def setup():
    update()
    add_nginx()
    add_python()
    set_wwwuser()
    add_redis()
    add_node()