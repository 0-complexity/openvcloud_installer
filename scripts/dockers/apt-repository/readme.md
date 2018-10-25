# Dockerfile
Using the Dockerfile the apt repository can be built, and should be pushed to the GIG docker image repository

# Apt packages management
The apt packages are maintained on ftp.gig.tech:/images/repo

# Using the apt repository
Place a file in /etc/apt/sources.list.d containing the following:
```apt
deb http://localhost binary/
```

Off course "localhost" needs to be replaced with ip:port combination exported by kubernetes for exposing the nginx listening internally on port 80.