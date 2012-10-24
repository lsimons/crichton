Set up for development:
    Install MySQL. You can use puppet to install MySQL the way its installed on the server,
      by following puppet-snippets/README.txt.
    If you don't use puppet, change MySQL to use InnoDB by default if needed - edit /etc/my.cnf:
            [mysqld]
            ...
            default-storage-engine = InnoDB
    If you don't use puppet, change MySQL to have a large-enough max_allowed_packet:
            [mysqld]
            ...
            max_allowed_packet = 128M
    Start MySQL.
    Make sure python is >=2.4.3.
    Install python-devel.
        If you have bbc python (like on sandbox), yum is confused about what to install,
        and things are pretty messed up. You should follow
          https://confluence.dev.domain.com/display/socom/crichton+on+the+sandbox
        to work around that.
    Install dependencies for the mysql module for python:
        yum install python-devel mysql-devel zlib-devel openssl-devel
    Install dependencies from ../vendor. (see ../vendor/README.txt).
    Follow crichtonweb/README.txt to get that up and running.
    
    To get SSL support working:
        Install standard/base forge httpd.
        Follow puppet-snippets/README.txt.

Set up on server:
    Upgrade to latest patched RHEL 5.
    Install standard/base forge httpd.
    Create a server cert at
        /etc/crichton.dev.domain.com.{key,pem}
        (unless you are on the sandbox).
    Follow puppet-snippets/README.txt.
    Done.

Set up on client:
    Upgrade to latest patched RHEL 5.
    yum install crichtonweb crichtoncli.
    TODO: crichton.py picks up configuration to talk to remote crichton server.
