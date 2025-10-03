// Academic Authenticity Validator - JavaScript Interface
class AcademicValidator {
    constructor() {
        this.currentTab = 'dashboard';
        this.audioEnabled = true;
        this.theme = 'dark';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDashboard();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Tab navigation
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // Theme toggle
        document.getElementById('themeToggle').addEventListener('click', () => {
            this.toggleTheme();
        });

        // Audio toggle
        document.getElementById('audioToggle').addEventListener('click', () => {
            this.toggleAudio();
        });

        // Modal controls
        document.querySelectorAll('.close-modal').forEach(btn => {
            btn.addEventListener('click', () => {
                this.closeModal();
            });
        });

        // Form submissions
        this.setupFormHandlers();
        this.setupSearchHandlers();
        this.setupVerificationHandlers();
        this.setupBlockchainHandlers();
    }

    switchTab(tabName) {
        // Update active tab
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Show tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabName).classList.add('active');

        this.currentTab = tabName;
        this.loadTabContent(tabName);
    }

    async loadTabContent(tabName) {
        this.showLoading();
        try {
            switch(tabName) {
                case 'dashboard':
                    await this.loadDashboard();
                    break;
                case 'credentials':
                    await this.loadCredentials();
                    break;
                case 'institutions':
                    await this.loadInstitutions();
                    break;
                case 'students':
                    break; // Loaded on search
                case 'research':
                    await this.loadResearchPapers();
                    break;
                case 'verification':
                    break; // Interactive verification
                case 'blockchain':
                    await this.loadBlockchain();
                    break;
            }
        } catch (error) {
            this.showNotification('Error loading content', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async loadDashboard() {
        try {
            // Show loading state
            this.showLoadingState();
            
            const response = await fetch('/api/dashboard');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Update stats with animation
            this.animateCounter('totalCredentials', data.total_credentials || 0);
            this.animateCounter('verifiedInstitutions', data.verified_institutions || 0);
            this.animateCounter('registeredStudents', data.registered_students || 0);
            this.animateCounter('researchPapers', data.research_papers || 0);
            
            // Update recent credentials
            this.updateRecentCredentials(data.recent_credentials || []);
            
            // Hide loading state
            this.hideLoadingState();
            
        } catch (error) {
            console.error('Error loading dashboard:', error);
            this.hideLoadingState();
            this.showNotification('Dashboard loaded with default data', 'info');
            
            // Load default data
            this.loadDefaultDashboard();
        }
    }

    showLoadingState() {
        const stats = document.querySelectorAll('.stat-card .stat-number');
        stats.forEach(stat => {
            stat.textContent = '...';
            stat.classList.add('loading');
        });
    }
    
    hideLoadingState() {
        const stats = document.querySelectorAll('.stat-card .stat-number');
        stats.forEach(stat => {
            stat.classList.remove('loading');
        });
    }
    
    animateCounter(elementId, targetValue) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const startValue = 0;
        const duration = 1000;
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const currentValue = Math.floor(startValue + (targetValue - startValue) * progress);
            element.textContent = currentValue;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }
    
    loadDefaultDashboard() {
        // Load with sample data
        this.animateCounter('totalCredentials', 156);
        this.animateCounter('verifiedInstitutions', 3);
        this.animateCounter('registeredStudents', 89);
        this.animateCounter('researchPapers', 23);
        
        this.updateRecentCredentials([
            {
                title: 'Bachelor of Computer Science',
                student_name: 'John Doe',
                institution_name: 'MIT',
                type: 'Degree',
                issue_date: new Date().toISOString()
            },
            {
                title: 'Machine Learning Certificate',
                student_name: 'Jane Smith',
                institution_name: 'Stanford',
                type: 'Certificate',
                issue_date: new Date(Date.now() - 86400000).toISOString()
            }
        ]);
    }
    
    updateRecentCredentials(credentials) {
        const container = document.getElementById('recentCredentials');
        if (!container) return;
        
        if (!credentials || credentials.length === 0) {
            container.innerHTML = '<p class="no-data">No recent credentials</p>';
            return;
        }
        
        container.innerHTML = credentials.map(cred => `
            <div class="credential-item">
                <div class="credential-info">
                    <h4>${cred.title}</h4>
                    <p>${cred.student_name} - ${cred.institution_name}</p>
                    <span class="credential-type">${cred.type}</span>
                </div>
                <div class="credential-date">
                    ${new Date(cred.issue_date).toLocaleDateString()}
                </div>
            </div>
        `).join('');
    }

    async loadCredentials() {
        try {
            const response = await fetch('/api/credentials/search', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({})
            });
            const data = await response.json();
            this.displayCredentials(data.results);
        } catch (error) {
            this.showNotification('Error loading credentials', 'error');
        }
    }

    displayCredentials(credentials) {
        const container = document.getElementById('credentialsList');
        if (!credentials || credentials.length === 0) {
            container.innerHTML = '<div class="credential-card">No credentials found</div>';
            return;
        }
        
        container.innerHTML = credentials.map(cred => `
            <div class="credential-card">
                <div class="card-header">
                    <div>
                        <div class="card-title">${cred.title}</div>
                        <div class="card-subtitle">${cred.student.first_name} ${cred.student.last_name}</div>
                    </div>
                    <button class="btn btn-secondary" onclick="validator.verifyCredential('${cred.id}')">
                        <i class="fas fa-shield-check"></i> Verify
                    </button>
                </div>
                <div class="card-content">
                    <div class="card-field">
                        <span class="field-label">Institution:</span>
                        <span class="field-value">${cred.institution.name}</span>
                    </div>
                    <div class="card-field">
                        <span class="field-label">Level:</span>
                        <span class="field-value">${cred.level}</span>
                    </div>
                    <div class="card-field">
                        <span class="field-label">Field:</span>
                        <span class="field-value">${cred.field_of_study}</span>
                    </div>
                    <div class="card-field">
                        <span class="field-label">ID:</span>
                        <span class="field-value">${cred.id}</span>
                    </div>
                </div>
            </div>
        `).join('');
    }

    async loadInstitutions() {
        try {
            const response = await fetch('/api/institutions');
            const institutions = await response.json();
            this.displayInstitutions(Object.values(institutions));
        } catch (error) {
            this.showNotification('Error loading institutions', 'error');
        }
    }

    displayInstitutions(institutions) {
        const container = document.getElementById('institutionsList');
        container.innerHTML = institutions.map(inst => `
            <div class="institution-card">
                <div class="card-header">
                    <div>
                        <div class="card-title">${inst.name}</div>
                        <div class="card-subtitle">${inst.country} - ${inst.type}</div>
                    </div>
                    <span class="btn ${inst.is_verified ? 'btn-success' : 'btn-warning'}">
                        <i class="fas fa-${inst.is_verified ? 'check-circle' : 'clock'}"></i>
                        ${inst.is_verified ? 'Verified' : 'Pending'}
                    </span>
                </div>
                <div class="card-content">
                    <div class="card-field">
                        <span class="field-label">ID:</span>
                        <span class="field-value">${inst.id}</span>
                    </div>
                    <div class="card-field">
                        <span class="field-label">Established:</span>
                        <span class="field-value">${inst.established_year}</span>
                    </div>
                    <div class="card-field">
                        <span class="field-label">Website:</span>
                        <span class="field-value"><a href="${inst.website}" target="_blank">${inst.website}</a></span>
                    </div>
                </div>
            </div>
        `).join('');
    }

    async loadResearchPapers() {
        try {
            const response = await fetch('/api/research-papers');
            if (response.ok) {
                const papers = await response.json();
                this.displayResearchPapers(papers);
            } else {
                document.getElementById('researchPapers').innerHTML = '<div class="paper-card">No research papers found</div>';
            }
        } catch (error) {
            document.getElementById('researchPapers').innerHTML = '<div class="paper-card">No research papers found</div>';
        }
    }

    displayResearchPapers(papers) {
        const container = document.getElementById('researchPapers');
        if (!papers || papers.length === 0) {
            container.innerHTML = '<div class="paper-card">No research papers found</div>';
            return;
        }
        
        container.innerHTML = papers.map(paper => `
            <div class="paper-card">
                <div class="card-title">${paper.title}</div>
                <div class="card-subtitle">Authors: ${paper.authors.join(', ')}</div>
                <div class="card-content">
                    <div class="card-field">
                        <span class="field-label">DOI:</span>
                        <span class="field-value">${paper.doi || 'N/A'}</span>
                    </div>
                    <div class="card-field">
                        <span class="field-label">Journal:</span>
                        <span class="field-value">${paper.journal || 'N/A'}</span>
                    </div>
                </div>
            </div>
        `).join('');
    }

    async loadBlockchain() {
        try {
            const [chainResponse, statsResponse] = await Promise.all([
                fetch('/api/chain'),
                fetch('/api/statistics')
            ]);
            
            const chain = await chainResponse.json();
            const stats = await statsResponse.json();
            
            // Update blockchain stats
            document.getElementById('chainLength').textContent = stats.blockchain_length;
            document.getElementById('pendingTx').textContent = stats.pending_transactions || 0;
            document.getElementById('chainValid').textContent = stats.is_valid ? 'Valid' : 'Invalid';
            
            // Display blockchain
            this.displayBlockchain(chain);
            
        } catch (error) {
            this.showNotification('Error loading blockchain', 'error');
        }
    }

    displayBlockchain(chain) {
        const container = document.getElementById('blockchainExplorer');
        container.innerHTML = chain.map((block, index) => `
            <div class="block-card">
                <div class="card-header">
                    <div class="card-title">Block #${index}</div>
                    <div class="card-subtitle">Hash: ${block.hash.substring(0, 16)}...</div>
                </div>
                <div class="card-content">
                    <div class="card-field">
                        <span class="field-label">Timestamp:</span>
                        <span class="field-value">${new Date(block.timestamp * 1000).toLocaleString()}</span>
                    </div>
                    <div class="card-field">
                        <span class="field-label">Transactions:</span>
                        <span class="field-value">${Array.isArray(block.data) ? block.data.length : 1}</span>
                    </div>
                    <div class="card-field">
                        <span class="field-label">Nonce:</span>
                        <span class="field-value">${block.nonce}</span>
                    </div>
                </div>
            </div>
        `).join('');
    }

    setupFormHandlers() {
        // Issue credential button
        const issueBtn = document.getElementById('issueCredentialBtn');
        if (issueBtn) {
            issueBtn.addEventListener('click', () => {
                this.showModal('issueCredentialModal');
                this.loadInstitutionOptions();
            });
        }

        // Issue credential form
        const issueForm = document.getElementById('issueCredentialForm');
        if (issueForm) {
            issueForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.issueCredential();
            });
        }
    }

    setupSearchHandlers() {
        // Credential search
        const credSearchBtn = document.getElementById('searchCredentialsBtn');
        if (credSearchBtn) {
            credSearchBtn.addEventListener('click', () => {
                this.searchCredentials();
            });
        }

        // Student search
        const studentSearchBtn = document.getElementById('searchStudentBtn');
        if (studentSearchBtn) {
            studentSearchBtn.addEventListener('click', () => {
                this.searchStudent();
            });
        }
    }

    setupVerificationHandlers() {
        const verifyBtn = document.getElementById('verifyBtn');
        if (verifyBtn) {
            verifyBtn.addEventListener('click', () => {
                this.performVerification();
            });
        }
    }

    setupBlockchainHandlers() {
        const mineBtn = document.getElementById('mineBlockBtn');
        if (mineBtn) {
            mineBtn.addEventListener('click', () => {
                this.mineBlock();
            });
        }

        const validateBtn = document.getElementById('validateChainBtn');
        if (validateBtn) {
            validateBtn.addEventListener('click', () => {
                this.validateChain();
            });
        }
    }

    async loadInstitutionOptions() {
        try {
            const response = await fetch('/api/institutions');
            const institutions = await response.json();
            
            const select = document.getElementById('institutionSelect');
            if (select) {
                select.innerHTML = Object.values(institutions).map(inst => 
                    `<option value="${inst.id}">${inst.name}</option>`
                ).join('');
            }
        } catch (error) {
            this.showNotification('Error loading institutions', 'error');
        }
    }

    async issueCredential() {
        const form = document.getElementById('issueCredentialForm');
        const formData = new FormData(form);
        
        const credentialData = {
            credential_type: formData.get('credentialType') || document.getElementById('credentialType').value,
            title: formData.get('credentialTitle') || document.getElementById('credentialTitle').value,
            field_of_study: formData.get('fieldOfStudy') || document.getElementById('fieldOfStudy').value,
            level: formData.get('credentialLevel') || document.getElementById('credentialLevel').value,
            issue_date: Date.now() / 1000,
            completion_date: new Date(document.getElementById('completionDate').value).getTime() / 1000,
            gpa: document.getElementById('gpa').value || null,
            honors: document.getElementById('honors').value || null,
            institution: {
                id: document.getElementById('institutionSelect').value
            },
            student: {
                id: document.getElementById('studentId').value,
                first_name: document.getElementById('firstName').value,
                last_name: document.getElementById('lastName').value,
                email: document.getElementById('studentEmail').value,
                date_of_birth: document.getElementById('dateOfBirth').value,
                student_id: document.getElementById('studentId').value
            }
        };

        try {
            this.showLoading();
            
            // Trigger credential issuance VFX
            if (window.vfxSystem) {
                const modal = document.getElementById('issueCredentialModal');
                const rect = modal.getBoundingClientRect();
                window.vfxSystem.createCredentialIssuanceEffect(
                    rect.left + rect.width / 2,
                    rect.top + rect.height / 2
                );
            }
            
            const response = await fetch('/api/credentials', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(credentialData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Enhanced success feedback
                this.showNotification('Credential issued successfully!', 'success');
                
                // Generate animated QR code
                if (result.qr_code_data && window.qrGenerator) {
                    const qrContainer = document.createElement('div');
                    qrContainer.style.position = 'fixed';
                    qrContainer.style.top = '50%';
                    qrContainer.style.left = '50%';
                    qrContainer.style.transform = 'translate(-50%, -50%)';
                    qrContainer.style.zIndex = '2000';
                    qrContainer.style.background = 'white';
                    qrContainer.style.padding = '20px';
                    qrContainer.style.borderRadius = '10px';
                    qrContainer.style.boxShadow = '0 10px 30px rgba(0,0,0,0.3)';
                    
                    document.body.appendChild(qrContainer);
                    
                    window.qrGenerator.generate(JSON.stringify(result.qr_code_data), qrContainer);
                    
                    setTimeout(() => {
                        qrContainer.remove();
                    }, 3000);
                }
                
                // Screen flash effect
                if (window.vfxSystem) {
                    window.vfxSystem.createScreenFlash('#16a34a', 0.1);
                }
                
                this.closeModal();
                if (this.currentTab === 'credentials') {
                    this.loadCredentials();
                }
                form.reset();
            } else {
                this.showNotification(`Error: ${result.error}`, 'error');
            }
        } catch (error) {
            this.showNotification('Error issuing credential', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async searchCredentials() {
        const searchTerm = document.getElementById('credentialSearch').value;
        const query = searchTerm ? { student_name: searchTerm } : {};
        
        try {
            const response = await fetch('/api/credentials/search', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(query)
            });
            const data = await response.json();
            this.displayCredentials(data.results);
        } catch (error) {
            this.showNotification('Error searching credentials', 'error');
        }
    }

    async searchStudent() {
        const studentId = document.getElementById('studentSearchId').value;
        if (!studentId) {
            this.showNotification('Please enter a student ID', 'warning');
            return;
        }

        try {
            const response = await fetch(`/api/students/${studentId}`);
            if (response.ok) {
                const data = await response.json();
                this.displayStudentDetails(data);
            } else {
                document.getElementById('studentDetails').innerHTML = '<div class="credential-card">Student not found</div>';
            }
        } catch (error) {
            this.showNotification('Error searching student', 'error');
        }
    }

    displayStudentDetails(data) {
        const container = document.getElementById('studentDetails');
        container.innerHTML = `
            <div class="credential-card">
                <div class="card-header">
                    <div class="card-title">${data.student.first_name} ${data.student.last_name}</div>
                    <div class="card-subtitle">Total Credentials: ${data.total_credentials}</div>
                </div>
                <div class="card-content">
                    <div class="card-field">
                        <span class="field-label">Student ID:</span>
                        <span class="field-value">${data.student.student_id}</span>
                    </div>
                    <div class="card-field">
                        <span class="field-label">Email:</span>
                        <span class="field-value">${data.student.email}</span>
                    </div>
                </div>
            </div>
            <div class="credentials-list">
                ${data.credentials.map(cred => `
                    <div class="credential-card">
                        <div class="card-title">${cred.title}</div>
                        <div class="card-subtitle">${cred.institution.name}</div>
                        <div class="card-content">
                            <div class="card-field">
                                <span class="field-label">Level:</span>
                                <span class="field-value">${cred.level}</span>
                            </div>
                            <div class="card-field">
                                <span class="field-label">Field:</span>
                                <span class="field-value">${cred.field_of_study}</span>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    async performVerification() {
        const credentialId = document.getElementById('verifyCredentialId').value;
        if (!credentialId) {
            this.showNotification('Please enter a credential ID', 'warning');
            return;
        }

        try {
            const response = await fetch(`/api/credentials/${credentialId}/verify`);
            const result = await response.json();
            
            this.displayVerificationResult(result);
            
            if (result.valid) {
                this.showNotification('Credential verified successfully!', 'success');
            } else {
                this.showNotification(`Verification failed: ${result.error}`, 'error');
            }
        } catch (error) {
            this.showNotification('Error verifying credential', 'error');
        }
    }

    displayVerificationResult(result) {
        const container = document.getElementById('verificationResult');
        
        if (result.valid) {
            const cred = result.credential;
            container.innerHTML = `
                <div class="credential-card">
                    <div class="card-header">
                        <div class="card-title">✅ Valid Credential</div>
                        <div class="card-subtitle">Verified on Blockchain</div>
                    </div>
                    <div class="card-content">
                        <div class="card-field">
                            <span class="field-label">Title:</span>
                            <span class="field-value">${cred.title}</span>
                        </div>
                        <div class="card-field">
                            <span class="field-label">Student:</span>
                            <span class="field-value">${cred.student.first_name} ${cred.student.last_name}</span>
                        </div>
                        <div class="card-field">
                            <span class="field-label">Institution:</span>
                            <span class="field-value">${cred.institution.name}</span>
                        </div>
                        <div class="card-field">
                            <span class="field-label">Level:</span>
                            <span class="field-value">${cred.level}</span>
                        </div>
                    </div>
                </div>
            `;
        } else {
            container.innerHTML = `
                <div class="credential-card">
                    <div class="card-header">
                        <div class="card-title">❌ Invalid Credential</div>
                        <div class="card-subtitle">Verification Failed</div>
                    </div>
                    <div class="card-content">
                        <div class="card-field">
                            <span class="field-label">Error:</span>
                            <span class="field-value">${result.error}</span>
                        </div>
                    </div>
                </div>
            `;
        }
    }

    async verifyCredential(credentialId) {
        try {
            const response = await fetch(`/api/credentials/${credentialId}/verify`);
            const result = await response.json();
            
            if (result.valid) {
                this.showNotification('Credential verified successfully!', 'success');
            } else {
                this.showNotification(`Verification failed: ${result.error}`, 'error');
            }
        } catch (error) {
            this.showNotification('Error verifying credential', 'error');
        }
    }

    async mineBlock() {
        try {
            this.showLoading();
            
            // Trigger mining VFX
            if (window.vfxSystem) {
                const btn = document.getElementById('mineBlockBtn');
                const rect = btn.getBoundingClientRect();
                window.vfxSystem.createMiningEffect(
                    rect.left + rect.width / 2,
                    rect.top + rect.height / 2
                );
            }
            
            const response = await fetch('/api/mine', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({institution_id: 'MIT001'}) // Default miner
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('Block mined successfully!', 'success');
                
                // Add new block to 3D visualization
                if (window.blockchain3D) {
                    window.blockchain3D.addNewBlock({
                        transactions: result.transactions_count,
                        hash: result.block_hash
                    });
                }
                
                // Screen flash for mining success
                if (window.vfxSystem) {
                    window.vfxSystem.createScreenFlash('#f59e0b', 0.15);
                }
                
                this.loadBlockchain();
            } else {
                this.showNotification(`Mining failed: ${result.error}`, 'error');
            }
        } catch (error) {
            this.showNotification('Error mining block', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async validateChain() {
        try {
            const response = await fetch('/api/validate');
            const result = await response.json();
            
            if (result.is_valid) {
                this.showNotification('Blockchain is valid!', 'success');
            } else {
                this.showNotification('Blockchain validation failed!', 'error');
            }
            
            document.getElementById('chainValid').textContent = result.is_valid ? 'Valid' : 'Invalid';
        } catch (error) {
            this.showNotification('Error validating chain', 'error');
        }
    }

    drawNetworkVisualization() {
        const canvas = document.getElementById('networkCanvas');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;
        
        // Clear canvas
        ctx.clearRect(0, 0, width, height);
        
        // Draw network nodes (institutions)
        const nodes = [
            {x: 100, y: 100, label: 'MIT'},
            {x: 300, y: 150, label: 'Harvard'},
            {x: 200, y: 250, label: 'Stanford'}
        ];
        
        // Draw connections
        ctx.strokeStyle = '#60a5fa';
        ctx.lineWidth = 2;
        nodes.forEach((node, i) => {
            nodes.forEach((otherNode, j) => {
                if (i !== j) {
                    ctx.beginPath();
                    ctx.moveTo(node.x, node.y);
                    ctx.lineTo(otherNode.x, otherNode.y);
                    ctx.stroke();
                }
            });
        });
        
        // Draw nodes
        nodes.forEach(node => {
            ctx.fillStyle = '#2563eb';
            ctx.beginPath();
            ctx.arc(node.x, node.y, 20, 0, 2 * Math.PI);
            ctx.fill();
            
            ctx.fillStyle = '#ffffff';
            ctx.font = '12px Inter';
            ctx.textAlign = 'center';
            ctx.fillText(node.label, node.x, node.y + 4);
        });
    }

    showModal(modalId) {
        document.getElementById(modalId).classList.add('active');
    }

    closeModal() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('active');
        });
    }

    showLoading() {
        document.getElementById('loadingOverlay').classList.add('active');
    }

    hideLoading() {
        document.getElementById('loadingOverlay').classList.remove('active');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.getElementById('notifications').appendChild(notification);
        
        // Play enhanced audio and trigger VFX
        if (this.audioEnabled && window.enhancedAudio) {
            window.enhancedAudio.play(type);
        }
        
        // Trigger VFX based on notification type
        if (window.vfxSystem) {
            const rect = notification.getBoundingClientRect();
            const x = rect.left + rect.width / 2;
            const y = rect.top + rect.height / 2;
            
            switch(type) {
                case 'success':
                    window.vfxSystem.createVerificationSuccessEffect(x, y);
                    break;
                case 'error':
                    window.vfxSystem.createErrorEffect(x, y);
                    break;
                default:
                    window.vfxSystem.createDataFlowEffect(x - 50, y, x + 50, y);
            }
        }
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    toggleTheme() {
        this.theme = this.theme === 'dark' ? 'light' : 'dark';
        document.body.setAttribute('data-theme', this.theme);
        
        const icon = document.querySelector('#themeToggle i');
        icon.className = this.theme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';
    }

    toggleAudio() {
        this.audioEnabled = !this.audioEnabled;
        const icon = document.querySelector('#audioToggle i');
        icon.className = this.audioEnabled ? 'fas fa-volume-up' : 'fas fa-volume-mute';
    }

    startAutoRefresh() {
        setInterval(() => {
            if (this.currentTab === 'dashboard') {
                this.loadDashboard();
            }
        }, 30000); // Refresh every 30 seconds
    }
}

// Initialize the validator when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.validator = new AcademicValidator();
});
