# Dockerfile
FROM python:3.12-bookworm

# Install Open MPI + SSH for mpirun across containers
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      openmpi-bin openssh-server && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir mpi4py joblib scikit-learn

WORKDIR /app
# Copy your service + queue + config + model
COPY mpi_service.py queue_manager.py config.json fraud_rf_model.pkl /app/

# Set up SSHD (required for mpirun over containers)
RUN mkdir /var/run/sshd

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
