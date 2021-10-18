# Project of NYU Data Communication and Network Course

### 1. Introduction

This repository is about the DCN project of NYU. Students should implement a simple email clients/servers (SMTP, POP3) and HTTP servers based on Flask, and then deploy them using Docker and Kubernetes. There was a time that people can access the public IP address to experience how email clients and servers work. However, after the semester ends, the free account to access IBM Kubernetes server was also retracted by our teacher, thus you can only test those files locally, and the testing methods can be seen on Part 2. 

To access the whole document for the project, please visit this [link](https://pan.baidu.com/s/1ljjoMQ_mLbevYmUQLbtjCw ), the extraction code is **t0h6**.

<hr></hr>

**Public IP (Now aborted) :**	169.57.112.50

**Port Mapping:**

| Server Name | Local Port | k8s Port |
| :---------: | :--------: | :------: |
| AU (PORT1)  |    5000    |  30000   |
| AE (PORT2)  |    6000    |  30001   |
| BE (PORT3)  |    7000    |  30002   |
| BU (PORT4)  |   53533    |  30003   |



**Test case**

Alice send email:

http://169.57.112.50:30000/email?from=169.57.112.50:30001&to=169.57.112.50:30002&message=hi.



Bob retrieve email:

http://169.57.112.50:30003/email?from=169.57.112.50:30002

<hr></hr>

### 2. Test locally

First, run four web servers. In order to do this, you need to start four command line interfaces such as powershell or cmd. In each CLI, type the following commands: 

```shell
cd AU
python AU.py
```

```shell
cd AE
python AE.py
```

```shell
cd BE
python BE.py
```

```shell
cd BU
python BU.py
```



The port number of each server is shown as blow:

| Server Name | Port  |
| :---------: | :---: |
|     AU      | 5000  |
|     AE      | 6000  |
|     BE      | 7000  |
|     BU      | 53533 |



Then, use the following test case:

Alice send email:

```
http://localhost:5000/email?from=localhost:6000&to=localhost:7000&message=hi.
```



Bob retrieve email:

```
http://localhost:53533/email?from=localhost:7000
```



In this way, Alice sent a email with the content "hi." to Bob through her agent server AU, and Bob will read the email through his agent server BU during his spare time.



### 3. Deploy through Docker

#### 3.1 Use Dockerfile to build images

Suppose you are in the root directory of the project, then type in the following commands through CLI. Remember to change the parameters accordingly.

```shell
cd AU
docker build -t USERNAME/au:latest .

cd ../AE
docker build -t USERNAME/ae:latest .

cd ../BE
docker build -t USERNAME/be:latest .

cd ../BU
docker build -t USERNAME/bu:latest .
```



To see if you have already built the four images successfully, use the following command:

```shell
docker image ls
```



#### 3.2 Create Docker network

To get servers running within Docker containers communicate with each other, you should create a Docker network with the following command:

```shell
docker network create N_Name
```



#### 3.3 Run containers to start the servers

Once created network, run the containers by specifying the network name:

```shell
docker run --network N_Name --name C_Name -p PORT1:PORT1 -it USERNAME/au:latest
```

```shell
docker run --network N_Name --name C_Name -p PORT2:PORT2 -it USERNAME/ae:latest
```

```shell
docker run --network N_Name --name C_Name -p PORT3:PORT3 -it USERNAME/bu:latest
```

```shell
docker run --network N_Name --name C_Name -p PORT4:PORT4 -it USERNAME/be:latest
```



#### 3.4 Test server

Once the servers have started, use `docker inspect N_Name` command to see the IP address of AE and BE, then use the IP address of AE and BE instead of `localhost`.

Alice send email:

```shell
http://localhost:5000/email?from=IP_AE:6000&to=IP_BE:7000&message=hi.
```

Bob retrieve email:

```
http://localhost:53533/email?from=IP_BE:7000
```



### 4. Deploy through k8s

#### 4.1 Push your images to Docker Hub

```shell
docker login
docker push USERNAME/au:latest
docker push USERNAME/ae:latest
docker push USERNAME/be:latest
docker push USERNAME/bu:latest
```



#### 4.2 Run the YAML file (Remember, you need to connect to your k8s server first)

```
kubectl apply -f deploy_email.yml
```



#### 4.3 Access the servers through IBM's public IP address



Alice send email:

http://169.57.112.50:30000/email?from=169.57.112.50:30001&to=169.57.112.50:30002&message=hi.



Bob retrieve email:

http://169.57.112.50:30003/email?from=169.57.112.50:30002
