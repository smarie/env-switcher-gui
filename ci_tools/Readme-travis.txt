On Windows

1) Open git bash (not cmd)
2) Generate a new ssh key:

	ssh-keygen -t rsa -b 4096 -C "sylvain.marie@schneider-electric.com" -f github_travis_rsa_<an_id> (DO NOT provide any passphrase.)
	
3) On the github repository page, Settings > Deploy Keys > Add deploy key > add the PUBLIC generated key (ending by .pub)


Then on Linux (does not work on windows, https://github.com/travis-ci/travis-ci/issues/4746)

4) (only the first time) Install travis commandline 
  - install ruby using RVM : (DO NOT SU nor sudo)  

	> \curl -sSL https://get.rvm.io | bash -s stable --ruby
	> source /home/ubuntu/.rvm/scripts/rvm
	> rvm install ruby (this installs to /home/ubuntu/.rvm/src/ruby...)

  - then install travis commandline:
  
	> gem install travis

5) (only the first time) Setup a shared folder with the windows session so as to access the PRIVATE key (not ending with .pub) file. If possible it should be the git folder, so that travis automatically detects the git project

	
5) Use travis commandline (you have to be outside of the proxy for this, otherwise strange error ipaddr...)

	> cd to the shared folder (/media/...)
	> source /home/ubuntu/.rvm/scripts/rvm
	> set http_proxy=
	> set https_proxy=
	> travis login 	
	> travis encrypt-file -r smarie/<repo-name> <your_key>   (DO NOT USE --add option since it will remove all comments in your travis.yml file!)

6) follow the instructions on screen :
	- copy the line starting with 'openssl ...' to your travis.yml file. 
	- modify the relative path to the generated file by adding 'ci_tools/' in front of 'github_travis_rsa_...enc'.
	- git add the generated file 'github_travis_rsa_...enc' but DO NOT ADD the private key

7) Finally encrypt the PyPi password:

	> travis login
	> travis encrypt -r smarie/<repo-name> <pypi_password>
	- copy the resulting string in the travis.yml file under deploy > password > secure
