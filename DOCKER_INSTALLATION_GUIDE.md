# Docker Installation Guide for Windows

## ⚠️ Important: Docker is Required

Docker is essential for testing the containerization phase locally. You need to install it before proceeding.

---

## 🔧 System Requirements

### Windows 10/11 Requirements
- **Windows 10 Pro, Enterprise, or Education** (Build 19041 or later)
- **Windows 11** (any edition)
- **RAM:** At least 4GB (8GB recommended)
- **Disk Space:** At least 10GB free
- **Virtualization:** Must be enabled in BIOS

### Check Virtualization
```powershell
# Run as Administrator
Get-ComputerInfo | Select-Object HyperVRequirementVirtualizationFirmwareEnabled
```

If it returns `False`, enable Hyper-V in BIOS.

---

## 📥 Installation Steps

### Step 1: Download Docker Desktop

**Option A: Official Docker Website (Recommended)**
1. Go to: https://www.docker.com/products/docker-desktop
2. Click "Download for Windows"
3. Choose your Windows version (Intel or Apple Silicon)
4. Save the installer

**Option B: Direct Download Links**
- Windows (Intel): https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe
- Windows (ARM): https://desktop.docker.com/win/main/arm64/Docker%20Desktop%20Installer.exe

### Step 2: Run the Installer

1. Double-click `Docker Desktop Installer.exe`
2. Follow the installation wizard
3. Accept the license agreement
4. Choose installation location (default is fine)
5. Select "Install required Windows components for WSL 2"
6. Click "Install"
7. Wait for installation to complete (5-10 minutes)

### Step 3: Complete Setup

1. Restart your computer when prompted
2. Docker Desktop will start automatically
3. You may see a WSL 2 installation prompt - follow the instructions
4. Wait for Docker to fully initialize (check system tray icon)

### Step 4: Verify Installation

```powershell
# Open PowerShell and run:
docker --version
docker run hello-world
```

You should see:
```
Docker version 24.x.x (or higher)
Hello from Docker!
```

---

## 🐛 Troubleshooting

### Docker Command Not Found
```powershell
# Add Docker to PATH manually
$env:Path += ";C:\Program Files\Docker\Docker\resources\bin"

# Or restart PowerShell/Terminal
```

### WSL 2 Installation Failed
```powershell
# Run as Administrator
wsl --install
wsl --set-default-version 2
```

### Docker Desktop Won't Start
1. Restart Docker Desktop from system tray
2. Check if Hyper-V is enabled
3. Restart your computer
4. Reinstall Docker if issues persist

### Out of Memory
```powershell
# Increase Docker memory allocation
# Settings > Resources > Memory: Set to 4GB or higher
```

---

## ✅ Verify Installation

```powershell
# Check Docker version
docker --version

# Check Docker info
docker info

# Test with hello-world
docker run hello-world

# List images
docker images

# List containers
docker ps -a
```

---

## 🚀 Next Steps After Installation

### 1. Test Docker Compose
```powershell
# Check if docker-compose is installed
docker-compose --version

# If not installed, install it
docker compose version
```

### 2. Start Your Project Stack
```powershell
# Navigate to project directory
cd "C:\Users\azizi\Downloads\Projet tekup\phishing dectection aymen"

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 3. Test Services
```powershell
# Test API
curl http://localhost:8000/health

# Test Dashboard
curl http://localhost:3000

# Test Prometheus
curl http://localhost:9090

# Test Grafana
curl http://localhost:3001
```

---

## 📊 Docker Desktop Settings

### Recommended Configuration

**Resources Tab:**
- CPUs: 4 (or more if available)
- Memory: 4GB (8GB recommended)
- Swap: 1GB
- Disk image size: 50GB

**General Tab:**
- ✓ Start Docker Desktop when you log in
- ✓ Use WSL 2 based engine

**Docker Engine Tab:**
- Keep default settings

---

## 🔐 Security Notes

1. **Don't run as root** - Docker Desktop handles this
2. **Keep Docker updated** - Check for updates regularly
3. **Use .env files** - Never commit secrets to git
4. **Scan images** - Use `docker scan` for vulnerabilities

---

## 📚 Useful Docker Commands

```powershell
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f [service-name]

# Execute command in container
docker-compose exec [service-name] [command]

# Rebuild images
docker-compose build

# Remove everything
docker-compose down -v

# Check resource usage
docker stats

# Clean up unused images
docker image prune

# Clean up unused containers
docker container prune
```

---

## 🆘 Getting Help

### Official Resources
- Docker Documentation: https://docs.docker.com
- Docker Community: https://forums.docker.com
- Stack Overflow: Tag `docker`

### Common Issues
- Docker Desktop not starting: Restart computer
- Port already in use: Change port in docker-compose.yml
- Out of memory: Increase Docker memory allocation
- WSL 2 issues: Run `wsl --update`

---

## ✨ After Installation

Once Docker is installed and running:

1. **Test locally:**
   ```bash
   docker-compose up -d
   ```

2. **Access services:**
   - API: http://localhost:8000
   - Dashboard: http://localhost:3000
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3001

3. **Continue with testing:**
   - Follow `TESTING_CHECKLIST.md`
   - Follow `DEPLOYMENT_GUIDE.md`

---

## 📝 Installation Checklist

- [ ] Downloaded Docker Desktop
- [ ] Ran installer
- [ ] Restarted computer
- [ ] Verified installation: `docker --version`
- [ ] Tested with: `docker run hello-world`
- [ ] Configured Docker Desktop settings
- [ ] Started docker-compose stack
- [ ] Tested all services
- [ ] Ready to proceed with testing

---

**Once Docker is installed, you can proceed with testing the containerization phase!**

Need help? Check the troubleshooting section above or refer to the official Docker documentation.

