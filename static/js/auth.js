/*!
 * AMDEC & Gamme IA - JavaScript d'Authentification
 * Gestion de la connexion sécurisée TAQA Morocco
 */

// Configuration de l'authentification
const AuthConfig = {
    API_BASE_URL: '',
    VERIFICATION_TIMEOUT: 15 * 60, // 15 minutes en secondes
    ALLOWED_DOMAINS: ['taqa.ma'],
    CODE_LENGTH: 6,
    MAX_ATTEMPTS: 3
};

// État de l'authentification
const AuthState = {
    currentStep: 'email', // 'email' ou 'verification'
    userEmail: '',
    verificationSent: false,
    countdownTimer: null,
    timeRemaining: 0,
    attempts: 0
};

// Gestionnaire principal d'authentification
class AuthManager {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.setupValidation();
    }

    initializeElements() {
        // Étapes
        this.emailStep = document.getElementById('email-step');
        this.verificationStep = document.getElementById('verification-step');
        
        // Formulaires
        this.emailForm = document.getElementById('email-form');
        this.verificationForm = document.getElementById('verification-form');
        
        // Champs
        this.emailInput = document.getElementById('email');
        this.verificationInput = document.getElementById('verification-code');
        
        // Boutons
        this.sendCodeBtn = document.getElementById('send-code-btn');
        this.verifyBtn = document.getElementById('verify-btn');
        this.backBtn = document.getElementById('back-btn');
        this.resendBtn = document.getElementById('resend-btn');
        
        // Éléments d'affichage
        this.sentEmailDisplay = document.getElementById('sent-email');
        this.countdownDisplay = document.getElementById('countdown');
        this.messageContainer = document.getElementById('message-container');
        this.loadingOverlay = document.getElementById('loadingOverlay');
    }

    bindEvents() {
        // Événements de formulaires
        this.emailForm.addEventListener('submit', (e) => this.handleEmailSubmit(e));
        this.verificationForm.addEventListener('submit', (e) => this.handleVerificationSubmit(e));
        
        // Boutons de navigation
        this.backBtn.addEventListener('click', () => this.showEmailStep());
        this.resendBtn.addEventListener('click', () => this.resendCode());
        
        // Validation en temps réel
        this.emailInput.addEventListener('input', () => this.validateEmailRealTime());
        this.verificationInput.addEventListener('input', () => this.validateCodeRealTime());
        
        // Auto-formatage du code de vérification
        this.verificationInput.addEventListener('input', (e) => this.formatVerificationCode(e));
    }

    setupValidation() {
        // Validation du format email
        this.emailInput.addEventListener('blur', () => {
            const email = this.emailInput.value.trim();
            if (email) {
                this.validateEmail(email);
            }
        });
    }

    // ===================================
    // Gestion des étapes d'authentification
    // ===================================

    showEmailStep() {
        this.emailStep.style.display = 'block';
        this.verificationStep.style.display = 'none';
        
        AuthState.currentStep = 'email';
        this.emailInput.focus();
        
        // Arrêter le countdown si actif
        if (AuthState.countdownTimer) {
            clearInterval(AuthState.countdownTimer);
            AuthState.countdownTimer = null;
        }
    }

    showVerificationStep(email) {
        this.emailStep.style.display = 'none';
        this.verificationStep.style.display = 'block';
        
        AuthState.currentStep = 'verification';
        AuthState.userEmail = email;
        
        this.sentEmailDisplay.textContent = email;
        this.verificationInput.focus();
        
        // Démarrer le countdown
        this.startCountdown();
    }

    // ===================================
    // Validation des données
    // ===================================

    validateEmail(email) {
        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        
        if (!email) {
            return { valid: false, message: 'Email requis' };
        }
        
        if (!emailRegex.test(email)) {
            return { valid: false, message: 'Format d\'email invalide' };
        }
        
        const domain = email.toLowerCase().split('@')[1];
        if (!AuthConfig.ALLOWED_DOMAINS.includes(domain)) {
            return { 
                valid: false, 
                message: `Seuls les emails @${AuthConfig.ALLOWED_DOMAINS.join(', @')} sont autorisés` 
            };
        }
        
        return { valid: true, message: 'Email valide' };
    }

    validateEmailRealTime() {
        const email = this.emailInput.value.trim().toLowerCase();
        const validation = this.validateEmail(email);
        
        // Appliquer les classes de validation
        this.emailInput.classList.remove('real-time-valid', 'real-time-invalid');
        
        if (email.length > 0) {
            if (validation.valid) {
                this.emailInput.classList.add('real-time-valid');
                this.sendCodeBtn.disabled = false;
            } else {
                this.emailInput.classList.add('real-time-invalid');
                this.sendCodeBtn.disabled = true;
            }
        } else {
            this.sendCodeBtn.disabled = true;
        }
    }

    validateCode(code) {
        if (!code) {
            return { valid: false, message: 'Code requis' };
        }
        
        if (!/^\d{6}$/.test(code)) {
            return { valid: false, message: 'Le code doit contenir 6 chiffres' };
        }
        
        return { valid: true, message: 'Code valide' };
    }

    validateCodeRealTime() {
        const code = this.verificationInput.value.trim();
        const validation = this.validateCode(code);
        
        // Appliquer les classes de validation
        this.verificationInput.classList.remove('real-time-valid', 'real-time-invalid');
        
        if (code.length > 0) {
            if (validation.valid) {
                this.verificationInput.classList.add('real-time-valid');
                this.verifyBtn.disabled = false;
            } else {
                this.verificationInput.classList.add('real-time-invalid');
                this.verifyBtn.disabled = true;
            }
        } else {
            this.verifyBtn.disabled = true;
        }
    }

    formatVerificationCode(e) {
        let value = e.target.value.replace(/\D/g, ''); // Garder seulement les chiffres
        
        if (value.length > AuthConfig.CODE_LENGTH) {
            value = value.slice(0, AuthConfig.CODE_LENGTH);
        }
        
        e.target.value = value;
        
        // Auto-submit si code complet
        if (value.length === AuthConfig.CODE_LENGTH) {
            setTimeout(() => {
                if (this.validateCode(value).valid) {
                    this.handleVerificationSubmit(new Event('submit'));
                }
            }, 500);
        }
    }

    // ===================================
    // Gestion des formulaires
    // ===================================

    async handleEmailSubmit(e) {
        e.preventDefault();
        
        const email = this.emailInput.value.trim().toLowerCase();
        const validation = this.validateEmail(email);
        
        if (!validation.valid) {
            this.showMessage(validation.message, 'error');
            this.emailInput.classList.add('animate-error');
            setTimeout(() => this.emailInput.classList.remove('animate-error'), 500);
            return;
        }
        
        try {
            this.setLoading(true, 'Envoi du code de vérification...');
            
            const response = await this.apiRequest('/api/auth/send_code', {
                method: 'POST',
                body: JSON.stringify({ email: email })
            });
            
            this.setLoading(false);
            
            if (response.success) {
                this.showMessage(response.message, 'success');
                this.emailInput.classList.add('animate-success');
                
                setTimeout(() => {
                    this.showVerificationStep(email);
                }, 1000);
                
            } else {
                this.showMessage(response.message, 'error');
            }
            
        } catch (error) {
            this.setLoading(false);
            this.showMessage('Erreur lors de l\'envoi du code: ' + error.message, 'error');
        }
    }

    async handleVerificationSubmit(e) {
        e.preventDefault();
        
        const code = this.verificationInput.value.trim();
        const validation = this.validateCode(code);
        
        if (!validation.valid) {
            this.showMessage(validation.message, 'error');
            this.verificationInput.classList.add('animate-error');
            setTimeout(() => this.verificationInput.classList.remove('animate-error'), 500);
            return;
        }
        
        try {
            this.setLoading(true, 'Vérification du code...');
            
            const response = await this.apiRequest('/api/auth/login', {
                method: 'POST',
                body: JSON.stringify({ 
                    email: AuthState.userEmail,
                    verification_code: code 
                })
            });
            
            this.setLoading(false);
            
            if (response.success) {
                this.showMessage('Connexion réussie ! Redirection...', 'success');
                
                // Stocker le token de session
                if (response.session_token) {
                    localStorage.setItem('auth_token', response.session_token);
                }
                
                // Redirection vers l'application
                setTimeout(() => {
                    window.location.href = response.redirect_url || '/';
                }, 1500);
                
            } else {
                AuthState.attempts++;
                
                let message = response.message;
                if (AuthState.attempts >= AuthConfig.MAX_ATTEMPTS) {
                    message += ' Vous devez recommencer.';
                    setTimeout(() => this.showEmailStep(), 3000);
                }
                
                this.showMessage(message, 'error');
                this.verificationInput.classList.add('animate-error');
                this.verificationInput.value = '';
                this.verificationInput.focus();
                
                setTimeout(() => {
                    this.verificationInput.classList.remove('animate-error');
                }, 500);
            }
            
        } catch (error) {
            this.setLoading(false);
            this.showMessage('Erreur lors de la vérification: ' + error.message, 'error');
        }
    }

    // ===================================
    // Gestion du countdown
    // ===================================

    startCountdown() {
        AuthState.timeRemaining = AuthConfig.VERIFICATION_TIMEOUT;
        this.updateCountdownDisplay();
        
        AuthState.countdownTimer = setInterval(() => {
            AuthState.timeRemaining--;
            this.updateCountdownDisplay();
            
            if (AuthState.timeRemaining <= 0) {
                clearInterval(AuthState.countdownTimer);
                this.handleCountdownExpired();
            }
        }, 1000);
    }

    updateCountdownDisplay() {
        const minutes = Math.floor(AuthState.timeRemaining / 60);
        const seconds = AuthState.timeRemaining % 60;
        
        const display = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        this.countdownDisplay.textContent = display;
        
        // Changer la couleur selon le temps restant
        this.countdownDisplay.className = '';
        if (AuthState.timeRemaining <= 60) {
            this.countdownDisplay.classList.add('danger');
        } else if (AuthState.timeRemaining <= 300) { // 5 minutes
            this.countdownDisplay.classList.add('warning');
        }
    }

    handleCountdownExpired() {
        this.showMessage('Le code de vérification a expiré. Veuillez en demander un nouveau.', 'warning');
        this.resendBtn.style.display = 'block';
        this.verifyBtn.disabled = true;
    }

    // ===================================
    // Fonctions utilitaires
    // ===================================

    async resendCode() {
        if (!AuthState.userEmail) {
            this.showEmailStep();
            return;
        }
        
        try {
            this.setLoading(true, 'Renvoi du code...');
            
            const response = await this.apiRequest('/api/auth/send_code', {
                method: 'POST',
                body: JSON.stringify({ email: AuthState.userEmail })
            });
            
            this.setLoading(false);
            
            if (response.success) {
                this.showMessage('Nouveau code envoyé !', 'success');
                this.startCountdown();
                this.verificationInput.value = '';
                this.verificationInput.focus();
                AuthState.attempts = 0;
            } else {
                this.showMessage(response.message, 'error');
            }
            
        } catch (error) {
            this.setLoading(false);
            this.showMessage('Erreur lors du renvoi: ' + error.message, 'error');
        }
    }

    showMessage(message, type) {
        const alertTypes = {
            'success': 'alert-success',
            'error': 'alert-danger',
            'warning': 'alert-warning',
            'info': 'alert-info'
        };
        
        const icons = {
            'success': 'fas fa-check-circle',
            'error': 'fas fa-exclamation-triangle',
            'warning': 'fas fa-exclamation-circle',
            'info': 'fas fa-info-circle'
        };
        
        const alertClass = alertTypes[type] || 'alert-info';
        const iconClass = icons[type] || 'fas fa-info-circle';
        
        const alertHtml = `
            <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
                <i class="${iconClass} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        this.messageContainer.innerHTML = alertHtml;
        
        // Auto-dismiss après 8 secondes sauf pour les erreurs
        if (type !== 'error') {
            setTimeout(() => {
                const alert = this.messageContainer.querySelector('.alert');
                if (alert) {
                    alert.remove();
                }
            }, 8000);
        }
    }

    setLoading(isLoading, message = 'Traitement en cours...') {
        if (isLoading) {
            document.getElementById('loadingMessage').textContent = message;
            this.loadingOverlay.style.display = 'flex';
        } else {
            this.loadingOverlay.style.display = 'none';
        }
        
        // Désactiver/activer les boutons
        const buttons = [this.sendCodeBtn, this.verifyBtn, this.backBtn, this.resendBtn];
        buttons.forEach(btn => {
            if (btn) btn.disabled = isLoading;
        });
    }

    async apiRequest(endpoint, options = {}) {
        const url = AuthConfig.API_BASE_URL + endpoint;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        const finalOptions = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, finalOptions);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || `Erreur HTTP ${response.status}`);
            }
            
            return data;
            
        } catch (error) {
            console.error('Erreur API auth:', error);
            throw error;
        }
    }
}

// ===================================
// Fonctions globales
// ===================================

// Fonction globale pour afficher un message
function showMessage(message, type) {
    if (window.authManager) {
        window.authManager.showMessage(message, type);
    } else {
        console.log(`${type.toUpperCase()}: ${message}`);
    }
}

// Fonction pour vérifier le statut d'authentification
async function checkAuthStatus() {
    const token = localStorage.getItem('auth_token');
    if (!token) {
        return { authenticated: false };
    }
    
    try {
        const response = await fetch('/api/auth/status', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        return data;
        
    } catch (error) {
        console.error('Erreur vérification auth:', error);
        return { authenticated: false };
    }
}

// Fonction de déconnexion
async function logout() {
    const token = localStorage.getItem('auth_token');
    
    try {
        if (token) {
            await fetch('/api/auth/logout', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
        }
    } catch (error) {
        console.error('Erreur logout:', error);
    } finally {
        localStorage.removeItem('auth_token');
        window.location.href = '/auth/login?logout=success';
    }
}

// ===================================
// Initialisation
// ===================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔐 Interface d\'authentification TAQA initialisée');
    
    // Initialiser le gestionnaire d'authentification
    window.authManager = new AuthManager();
    
    // Vérifier si l'utilisateur est déjà connecté
    checkAuthStatus().then(status => {
        if (status.authenticated) {
            showMessage('Vous êtes déjà connecté. Redirection...', 'info');
            setTimeout(() => {
                window.location.href = '/';
            }, 2000);
        }
    });
    
    // Gestion de la fermeture de page
    window.addEventListener('beforeunload', function() {
        if (AuthState.countdownTimer) {
            clearInterval(AuthState.countdownTimer);
        }
    });
});

// Export pour utilisation dans d'autres scripts
window.AuthManager = AuthManager;
window.logout = logout;
window.checkAuthStatus = checkAuthStatus;