/*!
 * AMDEC & Gamme IA - JavaScript Principal
 * Gestion des interactions interface utilisateur
 */

// Configuration globale
const CONFIG = {
    API_BASE_URL: '',
    MAX_FILE_SIZE: 50 * 1024 * 1024, // 50MB
    ALLOWED_EXTENSIONS: ['.xlsx', '.xls'],
    UPLOAD_TIMEOUT: 300000 // 5 minutes
};

// État global de l'application
const AppState = {
    currentPage: 'index',
    uploadedFile: null,
    generatedAMDEC: null,
    generatedGamemme: null,
    components: {},
    isLoading: false
};

// ✅ NOUVEAU: Questions suggérées enrichies pour le chatbot
const CHATBOT_SUGGESTIONS = {
    // Questions sur la maintenance préventive
    maintenance: [
        "Comment faire la maintenance préventive d'un économiseur BT (tous composants inclus) ?",
        "Quelle est la fréquence de maintenance recommandée pour les surchauffeurs HT ?",
        "Quels sont les matériels nécessaires pour la maintenance d'un réchauffeur ?",
        "Comment planifier la maintenance selon la criticité AMDEC ?",
        "Quelles sont les étapes de maintenance d'un collecteur de sortie ?"
    ],
    
    // Questions sur la corrosion et défauts
    defauts: [
        "Comment détecter une corrosion par attaque caustique ?",
        "Qu'est-ce que la corrosion caustic attack et comment la prévenir ?",
        "Comment identifier une surchauffe long terme sur un tube porteur ?",
        "Quels sont les signes de fluage dans les surchauffeurs HT ?",
        "Comment diagnostiquer un acid attack sur les réchauffeurs ?",
        "J'ai un percement sur l'économiseur BT, que faire ?",
        "Comment réagir en cas de percement sur collecteur d'entrée ?"
    ],
    
    // Questions sur les composants critiques
    composants: [
        "Quels sont les composants critiques des surchauffeurs HT ?",
        "Quelles sont les zones sensibles d'un économiseur BT ?",
        "Comment identifier les points critiques d'un réchauffeur HT ?",
        "Quels sous-composants surveiller en priorité sur les collecteurs ?"
    ],
    
    // Questions sur les contrôles et inspections
    controles: [
        "Quels contrôles périodiques effectuer sur un réchauffeur BT ?",
        "Comment effectuer un contrôle par ultrasons sur les épingles ?",
        "Quelle méthode CND utiliser pour détecter les fissures ?",
        "Comment contrôler l'étanchéité d'un collecteur ?",
        "Quand faire une inspection endoscopique ?"
    ],
    
    // Questions sur l'analyse AMDEC
    amdec: [
        "Comment calculer la criticité F×G×D d'un défaut ?",
        "Que signifient les valeurs F, G et D dans l'analyse AMDEC ?",
        "Comment interpréter une criticité de 45 ?",
        "Quelle est la différence entre maintenance préventive et conditionnelle ?",
        "Comment prioriser les actions correctives selon la criticité ?"
    ],
    
    // Questions générales techniques
    general: [
        "Quelle est la différence entre économiseur BT et HT ?",
        "Comment fonctionne un surchauffeur dans une chaudière ?",
        "Quels sont les modes de défaillance courants des tubes ?",
        "Comment prévenir l'encrassement des surfaces d'échange ?",
        "Quelles sont les températures critiques à surveiller ?"
    ]
};

// Utilitaires
const Utils = {
    /**
     * Affiche une notification à l'utilisateur
     */
    showNotification: (message, type = 'info', duration = 5000) => {
        const notification = document.getElementById('notification') || Utils.createNotificationElement();
        const icon = notification.querySelector('.notification-icon');
        const messageEl = notification.querySelector('.notification-message');
        
        // Icônes selon le type
        const icons = {
            'success': 'fas fa-check-circle',
            'error': 'fas fa-exclamation-triangle',
            'warning': 'fas fa-exclamation-circle',
            'info': 'fas fa-info-circle'
        };
        
        // Classes CSS selon le type
        const classes = {
            'success': 'notification-success',
            'error': 'notification-error',
            'warning': 'notification-warning',
            'info': 'notification-info'
        };
        
        // Mettre à jour la notification
        icon.className = `notification-icon ${icons[type] || icons.info}`;
        messageEl.textContent = message;
        notification.className = `notification ${classes[type] || classes.info}`;
        
        // Afficher
        notification.style.display = 'block';
        setTimeout(() => notification.classList.add('show'), 10);
        
        // Masquer automatiquement
        if (duration > 0) {
            setTimeout(() => Utils.hideNotification(), duration);
        }
    },
    
    /**
     * Masque la notification
     */
    hideNotification: () => {
        const notification = document.getElementById('notification');
        if (notification) {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.style.display = 'none';
            }, 300);
        }
    },
    
    /**
     * Crée l'élément de notification s'il n'existe pas
     */
    createNotificationElement: () => {
        const existing = document.getElementById('notification');
        if (existing) return existing;
        
        const notification = document.createElement('div');
        notification.id = 'notification';
        notification.className = 'notification';
        notification.innerHTML = `
            <div class="notification-content">
                <i class="notification-icon"></i>
                <span class="notification-message"></span>
            </div>
            <button class="notification-close" onclick="Utils.hideNotification()">&times;</button>
        `;
        
        document.body.appendChild(notification);
        return notification;
    },
    
    /**
     * Affiche/masque l'overlay de chargement
     */
    setLoading: (isLoading, message = 'Traitement en cours...') => {
        AppState.isLoading = isLoading;
        const overlay = document.getElementById('loadingOverlay');
        const messageEl = document.getElementById('loadingMessage');
        
        if (overlay) {
            if (isLoading) {
                if (messageEl) messageEl.textContent = message;
                overlay.style.display = 'flex';
            } else {
                overlay.style.display = 'none';
            }
        }
    },
    
    /**
     * Formate la taille d'un fichier
     */
    formatFileSize: (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    /**
     * Valide un fichier
     */
    validateFile: (file) => {
        const errors = [];
        
        // Vérifier la taille
        if (file.size > CONFIG.MAX_FILE_SIZE) {
            errors.push(`Fichier trop volumineux (max ${Utils.formatFileSize(CONFIG.MAX_FILE_SIZE)})`);
        }
        
        // Vérifier l'extension
        const extension = '.' + file.name.split('.').pop().toLowerCase();
        if (!CONFIG.ALLOWED_EXTENSIONS.includes(extension)) {
            errors.push(`Extension non autorisée. Extensions supportées: ${CONFIG.ALLOWED_EXTENSIONS.join(', ')}`);
        }
        
        return errors;
    },
    
    /**
     * Effectue une requête API
     */
    apiRequest: async (endpoint, options = {}) => {
        const url = CONFIG.API_BASE_URL + endpoint;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        // Merger les options
        const finalOptions = { ...defaultOptions, ...options };
        
        // Si c'est FormData, supprimer Content-Type pour laisser le navigateur le définir
        if (options.body instanceof FormData) {
            delete finalOptions.headers['Content-Type'];
        }
        
        try {
            const response = await fetch(url, finalOptions);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `Erreur HTTP ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error('Erreur API:', error);
            throw error;
        }
    },

    /**
     * ✅ NOUVEAU: Génère des suggestions de questions enrichies pour le chatbot
     */
    generateChatbotSuggestions: (count = 6, categories = null) => {
        // Si pas de catégories spécifiées, utiliser toutes les catégories
        const categoriesToUse = categories || Object.keys(CHATBOT_SUGGESTIONS);
        
        let allSuggestions = [];
        
        // Collecter toutes les questions des catégories sélectionnées
        categoriesToUse.forEach(category => {
            if (CHATBOT_SUGGESTIONS[category]) {
                allSuggestions = allSuggestions.concat(CHATBOT_SUGGESTIONS[category]);
            }
        });
        
        // Mélanger les questions
        const shuffled = allSuggestions.sort(() => 0.5 - Math.random());
        
        // Retourner le nombre demandé
        return shuffled.slice(0, count);
    },

    /**
     * ✅ NOUVEAU: Obtient des suggestions par catégorie
     */
    getSuggestionsByCategory: (category, count = 3) => {
        if (CHATBOT_SUGGESTIONS[category]) {
            const suggestions = CHATBOT_SUGGESTIONS[category];
            return suggestions.slice(0, count);
        }
        return [];
    },

    /**
     * ✅ NOUVEAU: Recherche de suggestions par mots-clés
     */
    searchSuggestions: (keywords, count = 5) => {
        const keywordLower = keywords.toLowerCase();
        let matchingSuggestions = [];
        
        // Parcourir toutes les catégories
        Object.values(CHATBOT_SUGGESTIONS).forEach(categoryQuestions => {
            categoryQuestions.forEach(question => {
                if (question.toLowerCase().includes(keywordLower)) {
                    matchingSuggestions.push(question);
                }
            });
        });
        
        return matchingSuggestions.slice(0, count);
    }
};

// Gestionnaire d'upload de fichiers
const FileUpload = {
    /**
     * Initialise la zone d'upload
     */
    init: () => {
        const uploadArea = document.getElementById('upload-area');
        const fileInput = document.getElementById('file-input');
        
        if (uploadArea && fileInput) {
            // Gestion drag & drop
            uploadArea.addEventListener('dragover', FileUpload.handleDragOver);
            uploadArea.addEventListener('dragleave', FileUpload.handleDragLeave);
            uploadArea.addEventListener('drop', FileUpload.handleDrop);
            
            // Gestion click
            uploadArea.addEventListener('click', () => fileInput.click());
            
            // Gestion selection fichier
            fileInput.addEventListener('change', FileUpload.handleFileSelect);
        }
    },
    
    handleDragOver: (e) => {
        e.preventDefault();
        e.stopPropagation();
        e.currentTarget.classList.add('dragover');
    },
    
    handleDragLeave: (e) => {
        e.preventDefault();
        e.stopPropagation();
        e.currentTarget.classList.remove('dragover');
    },
    
    handleDrop: (e) => {
        e.preventDefault();
        e.stopPropagation();
        e.currentTarget.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            FileUpload.processFile(files[0]);
        }
    },
    
    handleFileSelect: (e) => {
        const files = e.target.files;
        if (files.length > 0) {
            FileUpload.processFile(files[0]);
        }
    },
    
    /**
     * Traite le fichier sélectionné
     */
    processFile: (file) => {
        // Valider le fichier
        const errors = Utils.validateFile(file);
        if (errors.length > 0) {
            Utils.showNotification(errors.join('\n'), 'error');
            return;
        }
        
        // Afficher les informations du fichier
        FileUpload.displayFileInfo(file);
        
        // Stocker le fichier
        AppState.uploadedFile = file;
        
        // Démarrer l'upload et le traitement
        FileUpload.uploadAndProcess(file);
    },
    
    /**
     * Affiche les informations du fichier
     */
    displayFileInfo: (file) => {
        const fileInfo = document.getElementById('file-info');
        const fileName = document.getElementById('file-name');
        const fileSize = document.getElementById('file-size');
        
        if (fileInfo && fileName && fileSize) {
            fileName.textContent = file.name;
            fileSize.textContent = Utils.formatFileSize(file.size);
            fileInfo.style.display = 'block';
        }
        
        // Masquer la zone d'upload
        const uploadArea = document.getElementById('upload-area');
        if (uploadArea) {
            uploadArea.style.display = 'none';
        }
    },
    
    /**
     * ✅ CORRIGÉ: Upload et traite le fichier avec chaînage automatique
     */
    uploadAndProcess: async (file) => {
        try {
            // Afficher la section de traitement
            const processingSection = document.getElementById('processing-section');
            if (processingSection) {
                processingSection.style.display = 'block';
            }
            
            // Simuler progression
            FileUpload.updateProgress(10, 'Upload du fichier...');
            
            // Créer FormData
            const formData = new FormData();
            formData.append('file', file);
            
            FileUpload.updateProgress(30, 'Analyse du fichier...');
            
            // Envoyer à l'API
            const response = await Utils.apiRequest('/api/upload_historique', {
                method: 'POST',
                body: formData
            });
            
            FileUpload.updateProgress(60, 'Génération AMDEC...');
            
            // Attendre un peu pour l'effet visuel
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // ✅ Progression pour gammes automatiques
            if (response.auto_gammes_generated) {
                FileUpload.updateProgress(90, 'Génération gammes automatiques...');
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
            
            FileUpload.updateProgress(100, 'Terminé !');
            
            // Masquer le traitement
            setTimeout(() => {
                if (processingSection) {
                    processingSection.style.display = 'none';
                }
                
                // ✅ Afficher les résultats enrichis
                FileUpload.displayEnhancedResults(response);
            }, 1000);
            
        } catch (error) {
            console.error('Erreur upload:', error);
            Utils.showNotification(`Erreur lors du traitement: ${error.message}`, 'error');
            
            // Masquer le traitement
            const processingSection = document.getElementById('processing-section');
            if (processingSection) {
                processingSection.style.display = 'none';
            }
        }
    },
    
    /**
     * Met à jour la barre de progression
     */
    updateProgress: (percent, message) => {
        const progressFill = document.getElementById('progress-fill');
        const statusElement = document.getElementById('processing-status');
        
        if (progressFill) {
            progressFill.style.width = `${percent}%`;
        }
        
        if (statusElement) {
            statusElement.textContent = message;
        }
    },
    
    /**
     * ✅ NOUVEAU: Affichage enrichi des résultats avec gammes automatiques
     */
    displayEnhancedResults: (response) => {
        const resultsSection = document.getElementById('results-section');
        const resultsSummary = document.getElementById('results-summary');
        const downloadBtn = document.getElementById('download-amdec');
        
        if (resultsSection) {
            resultsSection.style.display = 'block';
        }
        
        // ✅ Section gammes automatiques
        let gammeSection = '';
        if (response.auto_gammes_generated && response.gammes_count > 0) {
            const gammeLinks = response.gammes_files.map(file => 
                `<div class="col-md-6 mb-2">
                    <a href="/download/${file}" class="btn btn-outline-success btn-sm w-100">
                        <i class="fas fa-download me-2"></i>${file}
                    </a>
                </div>`
            ).join('');
            
            gammeSection = `
                <div class="col-12 mt-4">
                    <div class="card border-success">
                        <div class="card-header bg-success text-white">
                            <h6 class="mb-0">
                                <i class="fas fa-magic me-2"></i>Gammes Générées Automatiquement
                            </h6>
                        </div>
                        <div class="card-body">
                            <p class="mb-3">
                                <strong>${response.gammes_count}</strong> gammes de maintenance ont été générées 
                                automatiquement à partir de l'analyse AMDEC.
                            </p>
                            <div class="row">
                                ${gammeLinks}
                            </div>
                        </div>
                    </div>
                </div>
            `;
        } else if (response.auto_gammes_generated === false) {
            gammeSection = `
                <div class="col-12 mt-4">
                    <div class="card border-warning">
                        <div class="card-header bg-warning text-dark">
                            <h6 class="mb-0">
                                <i class="fas fa-exclamation-triangle me-2"></i>Gammes Non Générées
                            </h6>
                        </div>
                        <div class="card-body">
                            <p class="mb-3">
                                Les gammes automatiques n'ont pas pu être générées. 
                                Vous pouvez les générer manuellement.
                            </p>
                            <button class="btn btn-primary" onclick="generateManualGamemmes('${response.filename}')">
                                <i class="fas fa-tools me-2"></i>Générer Gammes Manuellement
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }
        
        if (resultsSummary) {
            resultsSummary.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <div class="result-card">
                            <h5><i class="fas fa-file-excel text-success"></i> AMDEC Générée</h5>
                            <p><strong>Fichier:</strong> ${response.filename}</p>
                            <p><strong>Lignes traitées:</strong> ${response.rows_processed}</p>
                            <p><strong>Entrées AMDEC:</strong> ${response.amdec_entries}</p>
                            <p><strong>Source:</strong> Historique d'arrêts</p>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="result-card">
                            <h5><i class="fas fa-chart-line text-primary"></i> Statistiques</h5>
                            <p><strong>Criticité moyenne:</strong> ${response.avg_criticality}</p>
                            <p><strong>Criticité max:</strong> ${response.max_criticality}</p>
                            <p><strong>Composants uniques:</strong> ${response.statistics?.unique_components || 'N/A'}</p>
                            <p><strong>Gammes auto:</strong> 
                                <span class="badge ${response.auto_gammes_generated ? 'bg-success' : 'bg-warning'}">
                                    ${response.auto_gammes_generated ? response.gammes_count + ' générées' : 'Non générées'}
                                </span>
                            </p>
                        </div>
                    </div>
                    ${gammeSection}
                </div>
            `;
        }
        
        if (downloadBtn) {
            downloadBtn.onclick = () => FileUpload.downloadFile(response.filename);
        }
        
        // Stocker les résultats
        AppState.generatedAMDEC = response;
        
        const message = response.auto_gammes_generated 
            ? `AMDEC générée avec succès ! ${response.gammes_count} gammes créées automatiquement.`
            : 'AMDEC générée avec succès !';
        
        Utils.showNotification(message, 'success', 8000);
        
        // Scroll vers les résultats
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    },
    
    /**
     * Télécharge un fichier
     */
    downloadFile: (filename) => {
        const url = `/download/${encodeURIComponent(filename)}`;
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.click();
    },
    
    /**
     * Supprime le fichier sélectionné
     */
    removeFile: () => {
        AppState.uploadedFile = null;
        
        // Réinitialiser l'interface
        const uploadArea = document.getElementById('upload-area');
        const fileInfo = document.getElementById('file-info');
        const fileInput = document.getElementById('file-input');
        
        if (uploadArea) uploadArea.style.display = 'block';
        if (fileInfo) fileInfo.style.display = 'none';
        if (fileInput) fileInput.value = '';
    }
};

// ✅ NOUVEAU: Fonction pour génération manuelle de gammes
function generateManualGamemmes(amdecFilename) {
    if (!amdecFilename) {
        Utils.showNotification('Nom de fichier AMDEC requis', 'error');
        return;
    }
    
    Utils.setLoading(true, 'Génération des gammes en cours...');
    
    fetch('/api/generate_gammes_from_amdec', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            amdec_filename: amdecFilename
        })
    })
    .then(response => response.json())
    .then(data => {
        Utils.setLoading(false);
        
        if (data.success) {
            // Afficher le succès avec liens de téléchargement
            const gammeLinks = data.gammes_files.map(file => 
                `<a href="/download/${file}" class="btn btn-sm btn-success me-2 mb-2">
                    <i class="fas fa-download me-1"></i>${file}
                </a>`
            ).join('');
            
            const successHtml = `
                <div class="alert alert-success">
                    <h6 class="alert-heading">
                        <i class="fas fa-check-circle me-2"></i>Gammes Générées avec Succès !
                    </h6>
                    <p class="mb-2">
                        <strong>${data.gammes_count}</strong> gammes de maintenance ont été générées.
                    </p>
                    <div class="mt-2">
                        ${gammeLinks}
                    </div>
                </div>
            `;
            
            // Remplacer l'alerte d'erreur par le succès
            const errorAlert = document.querySelector('.alert-warning');
            if (errorAlert) {
                errorAlert.outerHTML = successHtml;
            }
            
            Utils.showNotification(`${data.gammes_count} gammes générées avec succès !`, 'success');
        } else {
            Utils.showNotification('Erreur: ' + (data.error || 'Erreur inconnue'), 'error');
        }
    })
    .catch(error => {
        Utils.setLoading(false);
        console.error('Erreur:', error);
        Utils.showNotification('Erreur lors de la génération des gammes', 'error');
    });
}

// Gestionnaire des gammes de maintenance
const GamemManager = {
    /**
     * Initialise la gestion des gammes
     */
    init: () => {
        GamemManager.loadComponents();
        
        const componentSelect = document.getElementById('component-select');
        const subcomponentSelect = document.getElementById('subcomponent-select');
        const generateBtn = document.getElementById('generate-maintenance-btn');
        
        if (componentSelect) {
            componentSelect.addEventListener('change', GamemManager.onComponentChange);
        }
        
        if (subcomponentSelect) {
            subcomponentSelect.addEventListener('change', GamemManager.onSubcomponentChange);
        }
        
        if (generateBtn) {
            generateBtn.addEventListener('click', GamemManager.generateMaintenance);
        }
    },
    
    /**
     * Charge la liste des composants
     */
    loadComponents: async () => {
        try {
            const components = await Utils.apiRequest('/api/components');
            AppState.components = components;
            
            const componentSelect = document.getElementById('component-select');
            if (componentSelect) {
                // Vider les options existantes
                componentSelect.innerHTML = '<option value="">Sélectionnez un composant...</option>';
                
                // Ajouter les composants
                components.forEach(comp => {
                    const option = document.createElement('option');
                    option.value = comp.id;
                    option.textContent = comp.name;
                    componentSelect.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Erreur chargement composants:', error);
            Utils.showNotification('Erreur lors du chargement des composants', 'error');
        }
    },
    
    /**
     * Gère le changement de composant
     */
    onComponentChange: (e) => {
        const componentId = e.target.value;
        const subcomponentSelect = document.getElementById('subcomponent-select');
        const subcomponentGroup = document.getElementById('subcomponent-group');
        
        if (!componentId) {
            if (subcomponentGroup) subcomponentGroup.style.display = 'none';
            GamemManager.hideCriticalityInfo();
            return;
        }
        
        // Afficher le groupe sous-composant
        if (subcomponentGroup) {
            subcomponentGroup.style.display = 'block';
        }
        
        // Remplir les sous-composants
        if (subcomponentSelect) {
            subcomponentSelect.innerHTML = '<option value="">Sélectionnez un sous-composant...</option>';
            
            const component = AppState.components.find(c => c.id === componentId);
            if (component && component.subcomponents) {
                component.subcomponents.forEach(subcomp => {
                    const option = document.createElement('option');
                    option.value = subcomp.id;
                    option.textContent = subcomp.name;
                    subcomponentSelect.appendChild(option);
                });
            }
        }
        
        GamemManager.hideCriticalityInfo();
    },
    
    /**
     * ✅ CORRIGÉ: Gère le changement de sous-composant avec aperçu enrichi
     */
    onSubcomponentChange: (e) => {
        const subcomponentId = e.target.value;
        const componentId = document.getElementById('component-select').value;
        
        if (!componentId || !subcomponentId) {
            GamemManager.hideCriticalityInfo();
            return;
        }
        
        // ✅ Calculer avec aperçu enrichi
        GamemManager.calculateCriticalityWithPreview(componentId, subcomponentId);
    },
    
    /**
     * ✅ NOUVEAU: Calcul de criticité avec aperçu des opérations
     */
    calculateCriticalityWithPreview: async (componentId, subcomponentId) => {
        try {
            const response = await Utils.apiRequest('/api/criticality', {
                method: 'POST',
                body: JSON.stringify({
                    component: componentId,
                    subcomponent: subcomponentId
                })
            });
            
            GamemManager.displayEnhancedCriticalityInfo(response, componentId, subcomponentId);
            
        } catch (error) {
            console.error('Erreur calcul criticité:', error);
            // Utiliser une valeur par défaut
            GamemManager.displayEnhancedCriticalityInfo({
                criticality: 25,
                level: 'Moyenne',
                description: 'Estimation par défaut'
            }, componentId, subcomponentId);
        }
    },
    
    /**
     * ✅ NOUVEAU: Affichage enrichi des informations de criticité
     */
    displayEnhancedCriticalityInfo: (data, componentId, subcomponentId) => {
        const criticalityInfo = document.getElementById('criticality-info');
        const criticalityValue = document.getElementById('criticality-value');
        const criticalityLabel = document.getElementById('criticality-label');
        const criticalityDescription = document.getElementById('criticality-description');
        const generateBtn = document.getElementById('generate-maintenance-btn');
        
        if (criticalityInfo) {
            criticalityInfo.style.display = 'block';
        }
        
        if (criticalityValue) {
            criticalityValue.textContent = data.criticality;
            
            // Couleur selon la criticité
            const colors = {
                'Négligeable': 'text-success',
                'Moyenne': 'text-warning', 
                'Élevée': 'text-warning',
                'Critique': 'text-danger'
            };
            
            criticalityValue.className = `criticality-value ${colors[data.level] || 'text-warning'}`;
        }
        
        if (criticalityLabel) {
            criticalityLabel.textContent = data.level;
        }
        
        // ✅ Description enrichie avec aperçu des opérations
        if (criticalityDescription) {
            const operationsPreview = GamemManager.getOperationsPreview(data.criticality);
            const timeEstimate = GamemManager.getTimeEstimate(data.criticality);
            
            criticalityDescription.innerHTML = `
                <div class="mb-3">${data.description}</div>
                <div class="small text-muted">
                    <strong>Aperçu de la gamme :</strong><br>
                    • Durée estimée : ${timeEstimate}<br>
                    • Opérations types : ${operationsPreview.join(', ')}<br>
                    • Fréquence recommandée : ${GamemManager.getFrequencyRecommendation(data.criticality)}
                </div>
            `;
        }
        
        if (generateBtn) {
            generateBtn.disabled = false;
            generateBtn.dataset.criticality = data.criticality;
            generateBtn.dataset.component = componentId;
            generateBtn.dataset.subcomponent = subcomponentId;
        }
    },
    
    /**
     * ✅ NOUVEAU: Aperçu des opérations selon criticité
     */
    getOperationsPreview: (criticality) => {
        if (criticality <= 12) {
            return ['Inspection visuelle', 'Contrôle de base'];
        } else if (criticality <= 16) {
            return ['Inspection', 'Mesures ultrasons', 'Nettoyage'];
        } else if (criticality <= 20) {
            return ['Inspection approfondie', 'Tests étanchéité', 'Traitement préventif'];
        } else {
            return ['Surveillance continue', 'Intervention corrective', 'Renforcement'];
        }
    },
    
    /**
     * ✅ NOUVEAU: Estimation du temps selon criticité
     */
    getTimeEstimate: (criticality) => {
        if (criticality <= 12) return '60-90 min';
        if (criticality <= 16) return '90-120 min';
        if (criticality <= 20) return '120-180 min';
        return '180-240 min';
    },
    
    /**
     * ✅ NOUVEAU: Fréquence recommandée selon criticité
     */
    getFrequencyRecommendation: (criticality) => {
        if (criticality <= 12) return 'Annuelle';
        if (criticality <= 16) return 'Semestrielle';
        if (criticality <= 20) return 'Trimestrielle';
        return 'Mensuelle';
    },
    
    /**
     * Masque les informations de criticité
     */
    hideCriticalityInfo: () => {
        const criticalityInfo = document.getElementById('criticality-info');
        const generateBtn = document.getElementById('generate-maintenance-btn');
        
        if (criticalityInfo) {
            criticalityInfo.style.display = 'none';
        }
        
        if (generateBtn) {
            generateBtn.disabled = true;
        }
    },
    
    /**
     * Génère une gamme de maintenance
     */
    generateMaintenance: async () => {
        const componentId = document.getElementById('component-select').value;
        const subcomponentId = document.getElementById('subcomponent-select').value;
        const generateBtn = document.getElementById('generate-maintenance-btn');
        const criticality = generateBtn.dataset.criticality;
        
        if (!componentId || !subcomponentId) {
            Utils.showNotification('Veuillez sélectionner un composant et un sous-composant', 'warning');
            return;
        }
        
        try {
            Utils.setLoading(true, 'Génération de la gamme de maintenance...');
            
            const response = await Utils.apiRequest('/api/generate_gamme', {
                method: 'POST',
                body: JSON.stringify({
                    component: componentId,
                    subcomponent: subcomponentId,
                    criticality: parseInt(criticality)
                })
            });
            
            Utils.setLoading(false);
            GamemManager.displayMaintenanceResults(response);
            
        } catch (error) {
            Utils.setLoading(false);
            console.error('Erreur génération gamme:', error);
            Utils.showNotification(`Erreur lors de la génération: ${error.message}`, 'error');
        }
    },
    
    /**
     * ✅ AMÉLIORÉ: Affichage des résultats de gamme avec détails enrichis
     */
    displayMaintenanceResults: (data) => {
        const resultsSection = document.getElementById('maintenance-results');
        const previewSection = document.getElementById('maintenance-preview');
        const downloadBtn = document.getElementById('download-maintenance');
        
        if (previewSection) {
            previewSection.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <div class="maintenance-summary-card">
                            <h5><i class="fas fa-tools text-success"></i> Gamme Générée</h5>
                            <p><strong>Composant:</strong> ${data.component_display}</p>
                            <p><strong>Sous-composant:</strong> ${data.subcomponent_display}</p>
                            <p><strong>Criticité:</strong> ${data.criticality} (${data.criticality_level})</p>
                            <p><strong>Fichier:</strong> ${data.filename}</p>
                            ${data.enhanced_with_amdec ? 
                                '<p><i class="fas fa-star text-warning"></i> <small>Enrichi avec données AMDEC</small></p>' : 
                                ''
                            }
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="maintenance-summary-card">
                            <h5><i class="fas fa-info-circle text-primary"></i> Détails Gamme</h5>
                            <p><strong>Opérations:</strong> ${data.operations_count}</p>
                            <p><strong>Temps estimé:</strong> ${data.estimated_time}</p>
                            <p><strong>Fréquence:</strong> ${data.frequency}</p>
                            <p><strong>Matériels:</strong> ${data.materials_count} types</p>
                            <p><strong>Consignes sécurité:</strong> ${data.safety_instructions}</p>
                        </div>
                    </div>
                </div>
                ${data.operations_preview && data.operations_preview.length > 0 ? `
                    <div class="row mt-3">
                        <div class="col-12">
                            <div class="maintenance-summary-card">
                                <h6><i class="fas fa-list me-2"></i>Aperçu des Opérations:</h6>
                                <ul class="list-unstyled">
                                    ${data.operations_preview.map(op => 
                                        `<li><i class="fas fa-check text-success me-2"></i>${op}</li>`
                                    ).join('')}
                                </ul>
                            </div>
                        </div>
                    </div>
                ` : ''}
            `;
        }
        
        if (downloadBtn) {
            downloadBtn.onclick = () => {
                window.open(`/download/${data.filename}`, '_blank');
            };
        }
        
        if (resultsSection) {
            resultsSection.style.display = 'block';
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }
        
        AppState.generatedGamemme = data;
        
        const message = data.enhanced_with_amdec 
            ? 'Gamme de maintenance générée et enrichie avec données AMDEC !'
            : 'Gamme de maintenance générée avec succès !';
        
        Utils.showNotification(message, 'success');
    }
};

// ✅ NOUVEAU: Gestion génération AMDEC depuis dataset
const DatasetManager = {
    /**
     * Génère AMDEC depuis dataset avec chaînage automatique
     */
    generateFromDataset: async () => {
        const componentSelect = document.getElementById('dataset-component-select');
        const subcomponentSelect = document.getElementById('dataset-subcomponent-select');
        
        if (!componentSelect || !subcomponentSelect) {
            console.warn('Éléments de sélection dataset non trouvés');
            return;
        }
        
        const component = componentSelect.value;
        const subcomponent = subcomponentSelect.value;
        
        if (!component) {
            Utils.showNotification('Veuillez sélectionner un composant', 'warning');
            return;
        }
        
        try {
            Utils.setLoading(true, 'Génération AMDEC depuis dataset...');
            
            const response = await Utils.apiRequest('/api/generate_amdec_from_dataset', {
                method: 'POST',
                body: JSON.stringify({
                    component: component,
                    subcomponent: subcomponent
                })
            });
            
            Utils.setLoading(false);
            DatasetManager.displayDatasetResults(response);
            
        } catch (error) {
            Utils.setLoading(false);
            console.error('Erreur génération AMDEC dataset:', error);
            Utils.showNotification(`Erreur: ${error.message}`, 'error');
        }
    },
    
    /**
     * ✅ NOUVEAU: Affichage enrichi des résultats dataset avec chaînage gammes
     */
    displayDatasetResults: (data) => {
        const resultsSection = document.getElementById('results-section');
        const resultsSummary = document.getElementById('results-summary');
        const downloadBtn = document.getElementById('download-amdec');
        
        // ✅ Affichage enrichi avec informations sur les gammes automatiques
        let gammeInfo = '';
        if (data.auto_gammes_generated) {
            gammeInfo = `
                <div class="alert alert-success mt-3">
                    <h6 class="alert-heading">
                        <i class="fas fa-magic me-2"></i>Gammes Générées Automatiquement !
                    </h6>
                    <p class="mb-1">
                        <strong>${data.gammes_count}</strong> gammes de maintenance ont été générées automatiquement 
                        à partir de l'AMDEC.
                    </p>
                    <div class="mt-2">
                        ${data.gammes_files.map(file => 
                            `<a href="/download/${file}" class="btn btn-sm btn-outline-success me-2">
                                <i class="fas fa-download me-1"></i>${file}
                            </a>`
                        ).join('')}
                    </div>
                </div>
            `;
        } else if (data.gamme_error) {
            gammeInfo = `
                <div class="alert alert-warning mt-3">
                    <h6 class="alert-heading">
                        <i class="fas fa-exclamation-triangle me-2"></i>Gammes Non Générées
                    </h6>
                    <p class="mb-1">Les gammes automatiques n'ont pas pu être générées.</p>
                    <button class="btn btn-sm btn-primary" onclick="generateManualGamemmes('${data.amdec_file}')">
                        <i class="fas fa-tools me-1"></i>Générer Gammes Manuellement
                    </button>
                </div>
            `;
        }
        
        if (resultsSummary) {
            resultsSummary.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <div class="result-card">
                            <h5><i class="fas fa-database text-success"></i> AMDEC depuis Dataset</h5>
                            <p><strong>Composant:</strong> ${data.component}</p>
                            <p><strong>Sous-composant:</strong> ${data.subcomponent}</p>
                            <p><strong>Entrées générées:</strong> ${data.entries_count}</p>
                            <p><strong>Source:</strong> Dataset d'expertise IA</p>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="result-card">
                            <h5><i class="fas fa-chart-pie text-primary"></i> Analyse</h5>
                            <p><strong>Criticité moyenne:</strong> ${data.avg_criticality}</p>
                            <p><strong>Criticité max:</strong> ${data.max_criticality}</p>
                            <p><strong>Gammes auto:</strong> 
                                <span class="badge ${data.auto_gammes_generated ? 'bg-success' : 'bg-warning'}">
                                    ${data.auto_gammes_generated ? 'Générées' : 'Non générées'}
                                </span>
                            </p>
                            <p><strong>Statut:</strong> <span class="badge bg-success">Succès</span></p>
                        </div>
                    </div>
                </div>
                ${gammeInfo}
            `;
        }
        
        if (downloadBtn) {
            downloadBtn.onclick = () => {
                window.open(`/download/${data.amdec_file}`, '_blank');
            };
        }
        
        if (resultsSection) {
            resultsSection.style.display = 'block';
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }
        
        const message = data.auto_gammes_generated 
            ? `AMDEC générée depuis dataset ! ${data.gammes_count} gammes créées automatiquement.`
            : 'AMDEC générée depuis dataset avec succès !';
        
        Utils.showNotification(message, 'success', 8000);
    }
};

// ✅ NOUVEAU: Gestionnaire pour le chatbot avec suggestions enrichies
const ChatbotManager = {
    /**
     * Initialise le gestionnaire de chatbot
     */
    init: () => {
        ChatbotManager.loadInitialSuggestions();
        ChatbotManager.setupSuggestionRefresh();
    },

    /**
     * Charge les suggestions initiales dans l'interface chatbot
     */
    loadInitialSuggestions: () => {
        const suggestionsContainer = document.getElementById('suggestions-list');
        if (!suggestionsContainer) return;

        // Générer 6 suggestions variées
        const suggestions = Utils.generateChatbotSuggestions(6);
        
        ChatbotManager.displaySuggestions(suggestions);
    },

    /**
     * Affiche les suggestions dans l'interface
     */
    displaySuggestions: (suggestions) => {
        const suggestionsContainer = document.getElementById('suggestions-list');
        if (!suggestionsContainer) return;

        const suggestionsHTML = suggestions.map(suggestion => `
            <div class="suggestion-item" onclick="ChatbotManager.fillQuestion('${suggestion.replace(/'/g, "\\'")}')">
                <i class="fas fa-lightbulb me-2 text-warning"></i>${suggestion}
            </div>
        `).join('');

        suggestionsContainer.innerHTML = suggestionsHTML || `
            <div class="text-center text-muted p-3">
                <small>Aucune suggestion disponible</small>
            </div>
        `;
    },

    /**
     * Remplit la zone de question avec une suggestion
     */
    fillQuestion: (question) => {
        const chatInput = document.getElementById('chat-input');
        if (chatInput) {
            chatInput.value = question;
            chatInput.focus();
            
            // Déclencher les événements pour mettre à jour l'interface
            chatInput.dispatchEvent(new Event('input'));
        }
    },

    /**
     * Configure le rafraîchissement automatique des suggestions
     */
    setupSuggestionRefresh: () => {
        // Rafraîchir les suggestions toutes les 2 minutes
        setInterval(() => {
            const suggestions = Utils.generateChatbotSuggestions(6);
            ChatbotManager.displaySuggestions(suggestions);
        }, 120000); // 2 minutes
    },

    /**
     * Met à jour les suggestions selon le contexte de la conversation
     */
    updateSuggestionsBasedOnContext: (detectedComponents, detectedDefects) => {
        let contextualSuggestions = [];

        // Suggestions basées sur les composants détectés
        if (detectedComponents && detectedComponents.length > 0) {
            detectedComponents.forEach(component => {
                if (component.includes('economiseur')) {
                    contextualSuggestions = contextualSuggestions.concat(
                        Utils.getSuggestionsByCategory('maintenance', 2),
                        Utils.getSuggestionsByCategory('controles', 1)
                    );
                } else if (component.includes('surchauffeur')) {
                    contextualSuggestions = contextualSuggestions.concat(
                        Utils.getSuggestionsByCategory('composants', 2),
                        Utils.getSuggestionsByCategory('defauts', 1)
                    );
                }
            });
        }

        // Suggestions basées sur les défauts détectés
        if (detectedDefects && detectedDefects.length > 0) {
            detectedDefects.forEach(defect => {
                if (defect.includes('corrosion')) {
                    contextualSuggestions = contextualSuggestions.concat(
                        Utils.getSuggestionsByCategory('defauts', 2)
                    );
                } else if (defect.includes('percement')) {
                    contextualSuggestions.push(
                        "Comment réagir en cas de percement sur collecteur d'entrée ?",
                        "Quels contrôles après réparation d'un percement ?"
                    );
                }
            });
        }

        // Supprimer les doublons et limiter
        const uniqueSuggestions = [...new Set(contextualSuggestions)].slice(0, 4);
        
        if (uniqueSuggestions.length > 0) {
            ChatbotManager.displaySuggestions(uniqueSuggestions);
        }
    }
};

// Gestionnaire de navigation
const Navigation = {
    /**
     * Initialise la navigation
     */
    init: () => {
        // Gestion des boutons de navigation
        document.querySelectorAll('[data-section]').forEach(button => {
            button.addEventListener('click', (e) => {
                const section = e.currentTarget.dataset.section;
                if (section) {
                    Navigation.showSection(section);
                }
            });
        });
        
        // Initialiser avec la section actuelle
        const currentPath = window.location.pathname;
        if (currentPath.includes('/amdec')) {
            Navigation.showSection('amdec');
        } else if (currentPath.includes('/gamme')) {
            Navigation.showSection('gamme');
        } else if (currentPath.includes('/chatbot')) {
            Navigation.showSection('chatbot');
        } else {
            Navigation.showSection('accueil');
        }
    },
    
    /**
     * Affiche une section spécifique
     */
    showSection: (sectionName) => {
        // Masquer toutes les sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });
        
        // Afficher la section demandée
        const targetSection = document.getElementById(sectionName);
        if (targetSection) {
            targetSection.classList.add('active');
        }
        
        // Mettre à jour les boutons de navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        document.querySelectorAll(`[data-section="${sectionName}"]`).forEach(btn => {
            btn.classList.add('active');
        });
        
        AppState.currentPage = sectionName;
        
        // Initialiser les fonctionnalités spécifiques à la section
        if (sectionName === 'amdec') {
            FileUpload.init();
        } else if (sectionName === 'gamme') {
            GamemManager.init();
        } else if (sectionName === 'chatbot') {
            ChatbotManager.init();
        }
    }
};

// Gestionnaire de modales
const Modal = {
    /**
     * Ouvre une modale
     */
    open: (modalId) => {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'block';
            setTimeout(() => modal.classList.add('show'), 10);
        }
    },
    
    /**
     * Ferme une modale
     */
    close: (modalId) => {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('show');
            setTimeout(() => {
                modal.style.display = 'none';
            }, 300);
        }
    },
    
    /**
     * Ferme toutes les modales
     */
    closeAll: () => {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('show');
            setTimeout(() => {
                modal.style.display = 'none';
            }, 300);
        });
    }
};

// ✅ Fonctions globales accessibles depuis HTML
window.removeFile = FileUpload.removeFile;
window.previewAmdec = () => Modal.open('preview-modal');
window.previewMaintenance = () => Modal.open('preview-modal');
window.closeModal = () => Modal.closeAll();
window.hideNotification = Utils.hideNotification;
window.switchSection = Navigation.showSection;
window.generateManualGamemmes = generateManualGamemmes;
window.generateFromDataset = DatasetManager.generateFromDataset;

// ✅ Fonction globale pour navigation vers génération de gammes
window.navigateToGamemmeGeneration = (component, subcomponent, criticality) => {
    window.location.href = `/gamme?component=${component}&subcomponent=${subcomponent}&criticality=${criticality}`;
};

// ✅ Auto-remplissage des paramètres URL
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 AMDEC & Gamme IA - Interface initialisée avec suggestions enrichies');
    
    // Initialiser les modules
    Navigation.init();
    
    // Initialiser selon la page actuelle
    if (AppState.currentPage === 'amdec') {
        FileUpload.init();
    } else if (AppState.currentPage === 'gamme') {
        GamemManager.init();
        
        // ✅ Vérifier si on est sur la page gamme avec des paramètres
        const urlParams = new URLSearchParams(window.location.search);
        const component = urlParams.get('component');
        const subcomponent = urlParams.get('subcomponent');
        const criticality = urlParams.get('criticality');
        
        if (component && document.getElementById('component-select')) {
            // Auto-remplir les sélections
            setTimeout(() => {
                document.getElementById('component-select').value = component;
                document.getElementById('component-select').dispatchEvent(new Event('change'));
                
                if (subcomponent) {
                    setTimeout(() => {
                        const subcompSelect = document.getElementById('subcomponent-select');
                        if (subcompSelect) {
                            subcompSelect.value = subcomponent;
                            subcompSelect.dispatchEvent(new Event('change'));
                        }
                    }, 500);
                }
            }, 100);
        }
    } else if (AppState.currentPage === 'chatbot') {
        // ✅ NOUVEAU: Initialiser le chatbot avec suggestions enrichies
        ChatbotManager.init();
    }
    
    // Gestion des clics sur overlay de modale
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            Modal.closeAll();
        }
    });
    
    // Gestion échappement pour fermer les modales
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            Modal.closeAll();
        }
    });
});

// Gestion des erreurs globales
window.addEventListener('error', (e) => {
    console.error('Erreur JavaScript:', e.error);
    Utils.showNotification('Une erreur inattendue s\'est produite', 'error');
});

// ✅ Export pour utilisation dans d'autres scripts avec ChatbotManager
window.AMDEC_APP = {
    Utils,
    FileUpload,
    GamemManager,
    DatasetManager,
    ChatbotManager,
    Navigation,
    Modal,
    AppState,
    CONFIG,
    CHATBOT_SUGGESTIONS
};