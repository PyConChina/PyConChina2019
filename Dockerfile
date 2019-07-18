FROM debian:latest
COPY requirements.txt /home/requirements.txt
RUN apt update && \
    apt upgrade -y && \
    apt install git zsh vim wget curl -y && \
    apt install python python-pip python-virtualenv -y && \
    apt install ruby ruby-dev -y && \
    apt install nodejs npm -y && \
    npm install uglify-js -g && \
    gem install sass && \
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)" "" --unattended && \
    pip install -r /home/requirements.txt
CMD ["/bin/zsh"]