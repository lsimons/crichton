Use in a simple way
-------------------
* Install puppet rpm.

    yum install puppet

* Check out ./development to /etc/puppet/development.

    cd /etc/puppet
    svn co /crichton/trunk/puppet-snippets/development

* Make sure your host (from `hostname -s`) is in /etc/puppet/development/site.pp
* Run

    cd /etc/puppet/development
    puppet --modulepath=/etc/puppet/development/modules --verbose --noop site.pp

* If no errors and it looks good, run

    cd /etc/puppet/development
    puppet --modulepath=/etc/puppet/development/modules --verbose site.pp

Use in complex way
------------------
Set up a puppet master locally, and then use with fancy puppet environment support, see

    Paste in SOCOM-69
    /Puppet+on+the+sandbox
