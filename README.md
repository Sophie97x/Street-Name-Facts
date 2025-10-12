# 🛣️ Street Names Explorer

An interactive web application that lets you explore the fascinating stories behind street names around the world. Click on any street on the map to discover its historical origins, powered by Wikipedia integration and intelligent pattern recognition.

## ✨ Features

- **Interactive World Map**: Explore streets anywhere in the world using OpenStreetMap
- **Wikipedia Integration**: Automatic fetching of street name origins from Wikipedia
- **Intelligent Fallbacks**: Smart pattern recognition for common street naming conventions
- **Location-Aware**: Provides context-specific information based on geographic location
- **Mobile Responsive**: Works seamlessly on desktop, tablet, and mobile devices
- **Real-time Facts**: Rotating collection of interesting street name facts
- **Enhanced Popups**: Rich, detailed information display with historical timelines

## 🚀 Quick Start with Docker

### Option 1: Docker Compose (Recommended)
```bash
# Clone or download the project
cd LocalCodeHub

# Build and start the application
docker-compose up -d

# Access the application
open http://localhost:8080
```

### Option 2: Docker Build
```bash
# Build the image
docker build -t street-names-explorer .

# Run the container
docker run -d \
  --name street-names-explorer \
  -p 8080:8080 \
  --restart unless-stopped \
  street-names-explorer

# Access the application
open http://localhost:8080
```

## 🖥️ Proxmox Deployment

### Prerequisites
- Proxmox VE server
- Docker installed on Proxmox host or in a VM/LXC container
- Port 8080 available

### Deployment Steps

1. **Upload Project Files**
   ```bash
   # Copy project to Proxmox host
   scp -r LocalCodeHub/ root@your-proxmox-ip:/opt/
   ```

2. **Deploy with Docker Compose**
   ```bash
   cd /opt/LocalCodeHub
   docker-compose up -d
   ```

3. **Configure Firewall (if needed)**
   ```bash
   # Allow port 8080 through Proxmox firewall
   iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
   ```

4. **Access Application**
   - Open browser and navigate to: `http://your-proxmox-ip:8080`
   - The application will be accessible on your local network

### Production Configuration

For production deployment, consider:

- **Reverse Proxy**: Use nginx or Apache to handle SSL/TLS
- **Domain Name**: Set up a domain name pointing to your Proxmox server
- **SSL Certificate**: Use Let's Encrypt for HTTPS
- **Resource Limits**: Configure Docker resource limits if needed

## 🛠️ Manual Installation

### Requirements
- Python 3.11+
- pip
- Internet connection (for Wikipedia API and map tiles)

### Installation Steps
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the application
cd backend
python server.py
```

## � Usage

1. **Search for a Location**: Enter any city, address, or landmark in the search box
2. **Find Streets**: Click "Find Streets" to load nearby streets on the map
3. **Explore Street Names**: Click on any colored street line to learn about its name
4. **Discover Facts**: Enjoy rotating street name facts in the sidebar
5. **Mobile Use**: Fully responsive design works on all devices

## 🌍 API Endpoints

- `GET /` - Main application interface
- `POST /api/search-location` - Search for geographic locations
- `POST /api/nearby-streets-enhanced` - Get streets near coordinates
- `POST /api/street-info-enhanced` - Get detailed street information
- `GET /api/health` - Health check endpoint

## 🔧 Configuration

### Environment Variables
- `FLASK_ENV=production` - Run in production mode
- `PYTHONUNBUFFERED=1` - Unbuffered Python output for Docker logs

### Port Configuration
Default port is 8080. To change:
- Update `docker-compose.yml` ports mapping
- Update `Dockerfile` EXPOSE directive
- Update server.py port configuration

## 📊 Monitoring

### Health Check
The application includes a health check endpoint at `/api/health`

### Docker Health Check
Built-in Docker health check monitors application status:
```bash
# Check container health
docker ps
# Look for "healthy" status
```

### Logs
```bash
# View application logs
docker-compose logs -f street-names-explorer

# View only recent logs
docker-compose logs --tail=50 street-names-explorer
```

## �️ Security

- Application runs on internal port 8080
- No authentication required (public information only)
- Uses HTTPS APIs for external data (Wikipedia, OpenStreetMap)
- Input validation on all user inputs
- Rate limiting handled by external APIs

## 🔄 Updates

To update the application:
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

## � Troubleshooting

### Common Issues

1. **Map not loading**: Check internet connection and firewall settings
2. **Port already in use**: Change port mapping in docker-compose.yml
3. **Container won't start**: Check Docker logs with `docker-compose logs`

### Debug Mode
To run in debug mode:
```bash
# Set environment variable
export FLASK_ENV=development

# Or run directly
cd backend
python server.py
```

## � Support

- Check application logs for error messages
- Verify all required ports are accessible
- Ensure Docker and Docker Compose are properly installed
- Check that the Proxmox host has internet connectivity

## 🎯 Performance

- **Memory Usage**: ~50-100MB per container
- **CPU Usage**: Minimal (<5% on modern hardware)
- **Network**: Requires internet for map tiles and Wikipedia data
- **Storage**: <100MB for application files

---

**Built with:** Python Flask, Leaflet.js, OpenStreetMap, Wikipedia API  
**Compatible with:** Docker, Proxmox VE, Linux, Windows, macOS  
**License:** Open source  

🛣️ **Happy Street Exploring!** 🗺️

This project is open source and available under the MIT License.

## 🐛 Troubleshooting

### Common Issues

**Port already in use**:
```bash
docker-compose down
docker-compose up -d
```

**Can't access from other machines**:
- Make sure port 8080 is open in your firewall
- Check that Docker is binding to 0.0.0.0:8080

**Slow map loading**:
- Check your internet connection
- OpenStreetMap tiles require internet access

### Health Check

Check if the service is running:
```bash
curl http://localhost:8080/api/health
```

## 🌍 Expand the Database

To add more streets, edit `backend/street_data.py`:

```python
"your_street_name": {
    "origin": "The story of how this street got its name...",
    "summary": "Brief description",
    "facts": [
        {"year": 1850, "fact": "Something interesting happened"},
        {"year": 1900, "fact": "Another historical fact"}
    ],
    "variations": ["alternative names"],
    "common_cities": ["City1", "City2"]
}
```

---

**Enjoy exploring the stories behind every street! 🛣️📚**