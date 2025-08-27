# 📊 Polling App

> A modern, responsive polling application built with Frappe Framework and Vue.js

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Frappe](https://img.shields.io/badge/Frappe-Framework-orange.svg)
![Vue.js](https://img.shields.io/badge/Vue.js-3.x-green.svg)

## ✨ Features

### 🎯 **Core Functionality**
- **Create Polls**: Easy-to-use interface for creating detailed polls
- **Smart Status Management**: Automatic handling of Active, Upcoming, and Ended polls
- **Real-time Participation**: Vote on active polls with instant feedback
- **Results Visualization**: View poll results with clear data presentation
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

### 🎨 **Modern UI/UX**
- **Clean Card-based Layout**: Professional, easy-to-scan poll cards
- **Emoji Icons**: Lightweight design without external icon dependencies
- **Status Indicators**: Color-coded badges for poll status (Active/Upcoming/Ended)
- **Loading States**: Smooth loading animations and empty state handling
- **Hover Effects**: Interactive elements with smooth transitions

### 🛠️ **Technical Features**
- **Frappe Framework Backend**: Robust, scalable backend with DocType management
- **Vue.js Frontend**: Modern, reactive frontend with Composition API
- **Production Ready**: CSRF token security for production deployments
- **Error Handling**: Comprehensive validation and user-friendly error messages
- **Tailwind CSS**: Utility-first styling for consistent design
- **Frappe UI Components**: Native integration with Frappe UI library
- **Date Management**: Smart date formatting and poll scheduling

## 🚀 Quick Start

### Prerequisites
- [Frappe Bench](https://github.com/frappe/bench) installed
- Node.js and Yarn for frontend development
- Python 3.8+ for backend

### Installation

1. **Get the app:**
```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/fawaaaz111/polling.git
```

2. **Install the app:**
```bash
bench install-app polling
```

3. **Start development (optional):**
```bash
# For backend development
bench start

# For frontend development
cd apps/polling/frontend
yarn dev
```

## 📱 Screenshots

### Polls Dashboard
- Clean, card-based layout showing all available polls
- Status badges indicating poll state
- Interactive voting and results buttons

### Poll Management
- Easy poll creation with title, description, and date settings
- Status tracking throughout poll lifecycle
- Responsive design for all devices

## 🏗️ Architecture

### Backend (Frappe Framework)
```
polling/
├── polling/
│   ├── doctype/
│   │   └── poll/          # Poll DocType with status management
│   ├── www/               # Web pages and API endpoints
│   └── public/            # Static assets
```

### Frontend (Vue.js)
```
frontend/
├── src/
│   ├── pages/
│   │   └── Polls.vue      # Main polls interface
│   ├── components/        # Reusable Vue components
│   └── router/            # Vue Router configuration
├── package.json           # Dependencies and scripts
└── vite.config.js         # Build configuration
```

## 🛠️ Development

### Setting up Development Environment

1. **Clone and install:**
```bash
bench get-app https://github.com/fawaaaz111/polling.git
bench install-app polling
```

2. **Enable developer mode:**
```bash
bench set-config developer_mode 1
```

3. **Start frontend development:**
```bash
cd apps/polling/frontend
yarn install
yarn dev
```

4. **Build for production:**
```bash
cd apps/polling/frontend
yarn build
# or
bench build --app polling
```

5. **Production deployment:**
```bash
# After building, restart your server
bench restart

# The app handles CSRF tokens automatically for secure production use
```

### Code Quality Tools

This app uses `pre-commit` for code formatting and linting:

```bash
cd apps/polling
pre-commit install
```

**Configured tools:**
- **ruff**: Python linting and formatting
- **eslint**: JavaScript/Vue.js linting
- **prettier**: Code formatting
- **pyupgrade**: Python syntax upgrading

## 📦 Dependencies

### Backend
- **Frappe Framework**: Core backend framework
- **Python 3.8+**: Runtime environment

### Frontend
- **Vue.js 3.x**: Progressive JavaScript framework
- **Tailwind CSS**: Utility-first CSS framework
- **Frappe UI**: Native Frappe component library
- **Vite**: Fast build tool and dev server

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Install pre-commit**: `pre-commit install`
4. **Make your changes** and ensure they pass all checks
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Development Guidelines
- Follow the existing code style and patterns
- Write clear commit messages
- Add comments for complex logic
- Test your changes thoroughly
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](license.txt) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/fawaaaz111/polling/issues)
- **Discussions**: [GitHub Discussions](https://github.com/fawaaaz111/polling/discussions)
- **Frappe Community**: [Frappe Forum](https://discuss.frappe.io/)

## 🙏 Acknowledgments

- [Frappe Framework](https://frappeframework.com/) for the robust backend
- [Vue.js](https://vuejs.org/) for the reactive frontend
- [Tailwind CSS](https://tailwindcss.com/) for the styling system
- [Frappe UI](https://github.com/frappe/frappe-ui) for native components

---

<div align="center">
  <strong>Built with ❤️ using Frappe Framework and Vue.js</strong>
</div>
