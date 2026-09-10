# TC6035 Part 1 — pinned execution environment
#
# This image is used for BOTH student development and autograding. That is not a
# convenience: the autograder re-executes a sample of each submission's runs and
# compares the values against what the student reported. In seeded stochastic
# search, one comparison flipping on a last-bit floating-point difference sends
# the search down a different branch, so an environment mismatch would flag an
# honest student as fabricating results.
#
# ---------------------------------------------------------------------------
# PLATFORM — the one-line switch
# ---------------------------------------------------------------------------
# Everyone must be on the SAME platform; which one is a cost trade, not a
# correctness question. Currently pinned to linux/amd64.
#
#   linux/amd64 (current)  base digest sha256:9c47360a2a0355e2da18516d0b1c2126ec22c195d2185e97347c9d98398c5bef
#   linux/arm64            base digest sha256:d04f49f5882f49a3b91f874e75e19f0c265f7222da8659741a9d7eab148f22a9
#
# To switch: change the digest on the FROM line below AND the `--platform` flag
# in devcontainer.json. Both must agree. See TOOLCHAIN.md for the trade-off.
# ---------------------------------------------------------------------------

FROM python@sha256:9c47360a2a0355e2da18516d0b1c2126ec22c195d2185e97347c9d98398c5bef

# --- Determinism -----------------------------------------------------------
# Multithreaded BLAS reorders floating-point reductions non-deterministically,
# which silently breaks bitwise reproducibility of seeded runs. Pinning every
# threading backend to a single thread is required, not an optimization choice.
ENV OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 \
    VECLIB_MAXIMUM_THREADS=1 \
    PYTHONHASHSEED=0 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# --- System packages -------------------------------------------------------
# git for submission history; the rest are build prerequisites for the
# scientific stack when a wheel is unavailable for the pinned platform.
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        build-essential \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# --- Python dependencies ---------------------------------------------------
COPY requirements.lock /tmp/requirements.lock
RUN python -m pip install --upgrade "pip==26.2.1" setuptools wheel \
    && python -m pip install --no-cache-dir -r /tmp/requirements.lock \
    && rm /tmp/requirements.lock

# --- Non-root user ---------------------------------------------------------
ARG USERNAME=student
ARG USER_UID=1000
ARG USER_GID=1000
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME
USER $USERNAME

WORKDIR /workspace
