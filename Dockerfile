FROM colynn/jenkins-jnlp-agent:base
USER root
COPY scripts_dev/  /home/admin/scripts_dev/

ENTRYPOINT ["jenkins-slave"]
