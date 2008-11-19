============================================
ABOUT
============================================

  RSOD (Reverse SSH On Demand) is web-based solution for facilitating the use
  of Reverse SSH.

============================================
INSTALL
============================================

  --- (1) - [ install web.py (http://webpy.org) ]

    RSOD is using the development version of web.py (which is 0.3), to get
    the development version installed:

        - wget http://github.com/webpy/webpy/tarball/master
        - tar -zxvf webpy-*.tar.gz
        - cd webpy-*
        - sudo python setup.py install

  --- (2) - [ install mako (http://makotemplates.org) ]

        - sudo easy_install mako
        - OR; sudo apt-get install python-mako
        - The first is preferred as it usually provides a more recent version.

  --- (3) - [ configuring ssh keys ]
    
    RSOD requires that firewall-ed machine to be able to access the remote host
    using SSH Keys (i.e. passwordless).

    On the firewall-ed machine do the following:

        - ssh-kegen
        - Enter an empty passphrase (just hit Enter when it prompts)
        - cat ~/.ssh/id_rsa.pub | ssh user@remotehost 'cat - >> ~/.ssh/authorized_keys'
  
  --- (4) - [ starting rsod ]

        - chmod +x rsod.py
        - ./rsod.py localhost:8080

============================================
LICENSE
============================================

  RSOD is licensed under GPL v3 or later. A copy of the license is included
  in this package.
