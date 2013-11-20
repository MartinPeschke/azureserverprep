azureserverprep
===============

sets up dependencies on an azure 12.04LTS server

all targets require a SUDOer user, e.g. azureuser and her ssh-key


execute targets like:

	fabric -H host.domain.com -u azureuser -i azureuser.key TARGET


Fabric Targets
===============

update
-------
update system packages

set_wwwuser
-----------
updates the www-user and adds bellerophons key for auto deployment


add_python
----------
updates system wide python  to the latest, 2.7.5 as of writing

add_nginx
------------------
adds latest nginx and updates RC (/server/nginx)

add_node
----------------
adds global nodejs for static item compiling




add_nginx_domain_config
-----------------------
answer questions and set up the nginx configuration for your website