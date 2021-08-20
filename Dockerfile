FROM 192.168.99.108:5000/library/jnlp-agent:base
USER root
COPY scripts_dev/  /home/admin/scripts_dev/

ENTRYPOINT ["jenkins-slave"]
