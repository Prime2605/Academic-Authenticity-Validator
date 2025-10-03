// Optimized Academic Validator - Performance Focused
class OptimizedAcademicValidator {
    constructor() {
        this.currentTab = 'dashboard';
        this.cache = new Map();
        this.debounceTimers = new Map();
        this.isLoading = false;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadDashboard();
        this.initializeMinimalVFX();
    }
    
    setupEventListeners() {
        // Tab navigation
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const tabName = btn.getAttribute('data-tab');
                this.switchTab(tabName);
            });
        });
        
        // Setup form handlers
        this.setupFormHandlers();
        
        // Load college data
        this.loadCollegeData();
    }
    
    setupFormHandlers() {
        // Issue credential form
        const issueForm = document.getElementById('issueCredentialForm');
        if (issueForm) {
            issueForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.debounce('issueCredential', () => this.issueCredential(), 500);
            });
        }
        
        // Verify credential form
        const verifyForm = document.getElementById('verifyCredentialForm');
        if (verifyForm) {
            verifyForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.debounce('verifyCredential', () => this.verifyCredential(), 500);
            });
        }
        
        // Mining button
        const mineBtn = document.getElementById('mineBlockBtn');
        if (mineBtn) {
            mineBtn.addEventListener('click', () => {
                this.debounce('mineBlock', () => this.mineBlock(), 1000);
            });
        }
    }
    
    debounce(key, func, delay) {
        if (this.debounceTimers.has(key)) {
            clearTimeout(this.debounceTimers.get(key));
        }
        
        const timer = setTimeout(() => {
            func();
            this.debounceTimers.delete(key);
        }, delay);
        
        this.debounceTimers.set(key, timer);
    }
    
    switchTab(tabName) {
        if (this.isLoading || this.currentTab === tabName) return;
        
        // Update active tab
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        // Show content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabName).classList.add('active');
        
        this.currentTab = tabName;
        
        // Load tab-specific data
        this.loadTabData(tabName);
    }
    
    async loadTabData(tabName) {
        if (this.cache.has(tabName)) {
            return; // Use cached data
        }
        
        switch (tabName) {
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
                await this.loadStudents();
                break;
            case 'research':
                await this.loadResearch();
                break;
            case 'blockchain':
                await this.loadBlockchain();
                break;
        }
    }
    
    async loadDashboard() {
        try {
            this.showLoading();
            
            // Try to load real data
            const response = await fetch('/api/dashboard');
            let data;
            
            if (response.ok) {
                data = await response.json();
            } else {
                // Use fallback data
                data = this.getFallbackDashboardData();
            }
            
            // Update UI with smooth animations
            this.updateDashboardStats(data);
            this.updateRecentCredentials(data.recent_credentials || []);
            
            this.cache.set('dashboard', data);
            
        } catch (error) {
            console.error('Dashboard error:', error);
            this.updateDashboardStats(this.getFallbackDashboardData());
            this.showNotification('Using demo data', 'info');
        } finally {
            this.hideLoading();
        }
    }
    
    getFallbackDashboardData() {
        return {
            total_credentials: 156,
            verified_institutions: 3,
            registered_students: 89,
            research_papers: 23,
            recent_credentials: [
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
            ]
        };
    }
    
    updateDashboardStats(data) {
        this.animateCounter('totalCredentials', data.total_credentials || 0);
        this.animateCounter('verifiedInstitutions', data.verified_institutions || 0);
        this.animateCounter('registeredStudents', data.registered_students || 0);
        this.animateCounter('researchPapers', data.research_papers || 0);
    }
    
    animateCounter(elementId, targetValue) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const startValue = parseInt(element.textContent) || 0;
        const duration = 800;
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const currentValue = Math.floor(startValue + (targetValue - startValue) * easeOutQuart);
            element.textContent = currentValue;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }
    
    updateRecentCredentials(credentials) {
        const container = document.getElementById('recentCredentials');
        if (!container) return;
        
        if (!credentials || credentials.length === 0) {
            container.innerHTML = '<div class="no-data">No recent credentials</div>';
            return;
        }
        
        container.innerHTML = credentials.map((cred, index) => `
            <div class="credential-item" style="animation-delay: ${index * 0.1}s">
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
        if (this.cache.has('credentials')) return;
        
        try {
            this.showLoading();
            const response = await fetch('/api/credentials/search', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({})
            });
            
            const data = response.ok ? await response.json() : { credentials: [] };
            this.displayCredentials(data.credentials);
            this.cache.set('credentials', data);
            
        } catch (error) {
            console.error('Credentials error:', error);
            this.displayCredentials([]);
        } finally {
            this.hideLoading();
        }
    }
    
    displayCredentials(credentials) {
        const container = document.getElementById('credentialsList');
        if (!container) return;
        
        if (!credentials || credentials.length === 0) {
            container.innerHTML = '<div class="no-data">No credentials found</div>';
            return;
        }
        
        container.innerHTML = credentials.map(cred => `
            <div class="credential-card">
                <h3>${cred.title}</h3>
                <p><strong>Student:</strong> ${cred.student_name}</p>
                <p><strong>Institution:</strong> ${cred.institution_name}</p>
                <p><strong>Type:</strong> ${cred.type}</p>
                <p><strong>Issue Date:</strong> ${new Date(cred.issue_date).toLocaleDateString()}</p>
                <div class="credential-actions">
                    <button onclick="validator.viewCredential('${cred.credential_id}')" class="btn-secondary">View</button>
                    <button onclick="validator.verifyCredential('${cred.credential_id}')" class="btn-primary">Verify</button>
                </div>
            </div>
        `).join('');
    }
    
    async loadInstitutions() {
        if (this.cache.has('institutions')) return;
        
        try {
            this.showLoading();
            const response = await fetch('/api/institutions');
            const data = response.ok ? await response.json() : { institutions: this.getFallbackInstitutions() };
            
            this.displayInstitutions(data.institutions);
            this.cache.set('institutions', data);
            
        } catch (error) {
            console.error('Institutions error:', error);
            this.displayInstitutions(this.getFallbackInstitutions());
        } finally {
            this.hideLoading();
        }
    }
    
    getFallbackInstitutions() {
        return [
            {
                institution_id: 'mit_001',
                name: 'Massachusetts Institute of Technology',
                location: 'Cambridge, MA',
                established: 1861,
                verified: true
            },
            {
                institution_id: 'harvard_001',
                name: 'Harvard University',
                location: 'Cambridge, MA',
                established: 1636,
                verified: true
            },
            {
                institution_id: 'stanford_001',
                name: 'Stanford University',
                location: 'Stanford, CA',
                established: 1885,
                verified: true
            }
        ];
    }
    
    displayInstitutions(institutions) {
        const container = document.getElementById('institutionsList');
        if (!container) return;
        
        container.innerHTML = institutions.map(inst => `
            <div class="institution-card">
                <h3>${inst.name}</h3>
                <p><strong>Location:</strong> ${inst.location}</p>
                <p><strong>Established:</strong> ${inst.established}</p>
                <div class="institution-status">
                    <span class="status ${inst.verified ? 'verified' : 'pending'}">
                        ${inst.verified ? '✓ Verified' : '⏳ Pending'}
                    </span>
                </div>
            </div>
        `).join('');
    }
    
    async loadStudents() {
        if (this.cache.has('students')) return;
        
        const fallbackStudents = [
            { student_id: 'std_001', name: 'John Doe', email: 'john@example.com', institution: 'MIT' },
            { student_id: 'std_002', name: 'Jane Smith', email: 'jane@example.com', institution: 'Stanford' },
            { student_id: 'std_003', name: 'Bob Johnson', email: 'bob@example.com', institution: 'Harvard' }
        ];
        
        this.displayStudents(fallbackStudents);
        this.cache.set('students', fallbackStudents);
    }
    
    displayStudents(students) {
        const container = document.getElementById('studentsList');
        if (!container) return;
        
        container.innerHTML = students.map(student => `
            <div class="student-card">
                <h3>${student.name}</h3>
                <p><strong>Email:</strong> ${student.email}</p>
                <p><strong>Institution:</strong> ${student.institution}</p>
                <div class="student-actions">
                    <button onclick="validator.viewStudent('${student.student_id}')" class="btn-secondary">View Profile</button>
                </div>
            </div>
        `).join('');
    }
    
    async loadResearch() {
        if (this.cache.has('research')) return;
        
        const fallbackResearch = [
            {
                paper_id: 'rp_001',
                title: 'Blockchain Applications in Education',
                authors: ['Dr. Smith', 'Prof. Johnson'],
                institution: 'MIT',
                publication_date: '2024-01-15'
            },
            {
                paper_id: 'rp_002',
                title: 'Digital Credentials and Trust Networks',
                authors: ['Dr. Brown', 'Dr. Davis'],
                institution: 'Stanford',
                publication_date: '2024-02-20'
            }
        ];
        
        this.displayResearch(fallbackResearch);
        this.cache.set('research', fallbackResearch);
    }
    
    displayResearch(papers) {
        const container = document.getElementById('researchList');
        if (!container) return;
        
        container.innerHTML = papers.map(paper => `
            <div class="research-card">
                <h3>${paper.title}</h3>
                <p><strong>Authors:</strong> ${paper.authors.join(', ')}</p>
                <p><strong>Institution:</strong> ${paper.institution}</p>
                <p><strong>Published:</strong> ${new Date(paper.publication_date).toLocaleDateString()}</p>
                <div class="research-actions">
                    <button onclick="validator.viewPaper('${paper.paper_id}')" class="btn-secondary">View Paper</button>
                </div>
            </div>
        `).join('');
    }
    
    async loadBlockchain() {
        if (this.cache.has('blockchain')) return;
        
        try {
            this.showLoading();
            const response = await fetch('/api/blockchain/info');
            const data = response.ok ? await response.json() : this.getFallbackBlockchainData();
            
            this.displayBlockchainInfo(data);
            this.cache.set('blockchain', data);
            
        } catch (error) {
            console.error('Blockchain error:', error);
            this.displayBlockchainInfo(this.getFallbackBlockchainData());
        } finally {
            this.hideLoading();
        }
    }
    
    getFallbackBlockchainData() {
        return {
            chain_length: 6,
            difficulty: 2,
            pending_transactions: 3,
            last_block_hash: '0079e0b35d53b4b322e1127af1dac3200accb8e50b531eb42c85aea17005c000'
        };
    }
    
    displayBlockchainInfo(data) {
        const container = document.getElementById('blockchainInfo');
        if (!container) return;
        
        container.innerHTML = `
            <div class="blockchain-stats">
                <div class="stat-item">
                    <h3>${data.chain_length}</h3>
                    <p>Total Blocks</p>
                </div>
                <div class="stat-item">
                    <h3>${data.difficulty}</h3>
                    <p>Mining Difficulty</p>
                </div>
                <div class="stat-item">
                    <h3>${data.pending_transactions}</h3>
                    <p>Pending Transactions</p>
                </div>
            </div>
            <div class="last-block">
                <h4>Latest Block Hash:</h4>
                <code>${data.last_block_hash}</code>
            </div>
        `;
    }
    
    async issueCredential() {
        if (this.isLoading) return;
        
        const form = document.getElementById('issueCredentialForm');
        const formData = new FormData(form);
        
        try {
            this.showLoading();
            this.showNotification('Issuing credential...', 'info');
            
            const response = await fetch('/api/credentials/issue', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    student_name: formData.get('studentName'),
                    student_email: formData.get('studentEmail'),
                    credential_title: formData.get('credentialTitle'),
                    credential_type: formData.get('credentialType'),
                    institution_id: formData.get('institutionId'),
                    grade: formData.get('grade') || 'A'
                })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showNotification('Credential issued successfully!', 'success');
                this.clearCache('credentials');
                this.clearCache('dashboard');
                form.reset();
                
                // Show QR code if available
                if (result.qr_code) {
                    this.showQRCode(result.qr_code);
                }
            } else {
                this.showNotification(result.error || 'Failed to issue credential', 'error');
            }
            
        } catch (error) {
            console.error('Issue credential error:', error);
            this.showNotification('Error issuing credential', 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    async verifyCredential() {
        if (this.isLoading) return;
        
        const form = document.getElementById('verifyCredentialForm');
        const credentialId = form.querySelector('[name="credentialId"]').value;
        
        if (!credentialId) {
            this.showNotification('Please enter a credential ID', 'warning');
            return;
        }
        
        try {
            this.showLoading();
            this.showNotification('Verifying credential...', 'info');
            
            const response = await fetch('/api/credentials/verify', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ credential_id: credentialId })
            });
            
            const result = await response.json();
            
            if (response.ok && result.valid) {
                this.showNotification('✓ Credential is valid and verified!', 'success');
                this.displayVerificationResult(result);
            } else {
                this.showNotification('✗ Credential verification failed', 'error');
            }
            
        } catch (error) {
            console.error('Verify credential error:', error);
            this.showNotification('Error verifying credential', 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    displayVerificationResult(result) {
        const container = document.getElementById('verificationResult');
        if (!container) return;
        
        container.innerHTML = `
            <div class="verification-success">
                <h3>✓ Verification Successful</h3>
                <p><strong>Title:</strong> ${result.credential.title}</p>
                <p><strong>Student:</strong> ${result.credential.student_name}</p>
                <p><strong>Institution:</strong> ${result.credential.institution_name}</p>
                <p><strong>Issue Date:</strong> ${new Date(result.credential.issue_date).toLocaleDateString()}</p>
                <p><strong>Block Hash:</strong> <code>${result.block_hash}</code></p>
            </div>
        `;
        container.style.display = 'block';
    }
    
    async mineBlock() {
        if (this.isLoading) return;
        
        try {
            this.showLoading();
            this.showNotification('Mining new block...', 'info');
            
            const response = await fetch('/api/blockchain/mine', {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showNotification(`Block mined successfully! Hash: ${result.block_hash.substring(0, 16)}...`, 'success');
                this.clearCache('blockchain');
                this.clearCache('dashboard');
            } else {
                this.showNotification('Mining failed', 'error');
            }
            
        } catch (error) {
            console.error('Mining error:', error);
            this.showNotification('Error mining block', 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    showQRCode(qrData) {
        const modal = document.getElementById('qrModal');
        const qrContainer = document.getElementById('qrCodeContainer');
        
        if (modal && qrContainer) {
            qrContainer.innerHTML = `<img src="data:image/png;base64,${qrData}" alt="QR Code" style="max-width: 100%;">`;
            modal.style.display = 'flex';
        }
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
    showLoading() {
        this.isLoading = true;
        const loader = document.getElementById('loadingOverlay');
        if (loader) loader.style.display = 'flex';
    }
    
    hideLoading() {
        this.isLoading = false;
        const loader = document.getElementById('loadingOverlay');
        if (loader) loader.style.display = 'none';
    }
    
    clearCache(key) {
        if (key) {
            this.cache.delete(key);
        } else {
            this.cache.clear();
        }
    }
    
    // College Database Integration
    async loadCollegeData() {
        try {
            // Load college categories and types for filters
            const [categoriesRes, typesRes, statsRes] = await Promise.all([
                fetch('/api/colleges/categories'),
                fetch('/api/colleges/types'),
                fetch('/api/colleges/stats')
            ]);
            
            const categories = await categoriesRes.json();
            const types = await typesRes.json();
            const stats = await statsRes.json();
            
            this.collegeCategories = categories.categories;
            this.collegeTypes = types.types;
            this.collegeStats = stats;
            
            // Populate institution dropdown
            await this.populateInstitutionDropdown();
            
            // Update dashboard with college stats
            this.updateCollegeStats();
            
        } catch (error) {
            console.error('Error loading college data:', error);
        }
    }
    
    async populateInstitutionDropdown() {
        const institutionSelect = document.getElementById('institutionId');
        if (!institutionSelect) return;
        
        try {
            const response = await fetch('/api/colleges/search', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({})
            });
            
            const data = await response.json();
            const colleges = data.colleges || [];
            
            // Clear existing options except the first one
            institutionSelect.innerHTML = '<option value="">Select Institution</option>';
            
            // Add colleges to dropdown
            colleges.forEach(college => {
                const option = document.createElement('option');
                option.value = college.institution_id;
                option.textContent = `${college.name} (${college.category})`;
                option.dataset.collegeData = JSON.stringify(college);
                institutionSelect.appendChild(option);
            });
            
        } catch (error) {
            console.error('Error loading institutions:', error);
            // Add fallback options
            this.addFallbackInstitutions(institutionSelect);
        }
    }
    
    addFallbackInstitutions(select) {
        const fallbackColleges = [
            { id: 'iitm_001', name: 'IIT Madras' },
            { id: 'loyola_001', name: 'Loyola College' },
            { id: 'iit_chennai_001', name: 'IIT Chennai' },
            { id: 'nie_001', name: 'National Institute of Epidemiology' },
            { id: 'bist_001', name: 'Bharath Institute of Science and Technology' }
        ];
        
        fallbackColleges.forEach(college => {
            const option = document.createElement('option');
            option.value = college.id;
            option.textContent = college.name;
            select.appendChild(option);
        });
    }
    
    updateCollegeStats() {
        // Update dashboard with college statistics
        if (this.collegeStats) {
            const totalCollegesElement = document.getElementById('totalColleges');
            if (totalCollegesElement) {
                this.animateCounter('totalColleges', this.collegeStats.total_institutions || 0);
            }
        }
    }
    
    // Enhanced institution selection with course loading
    async onInstitutionChange(institutionId) {
        const courseSelect = document.getElementById('credentialCourse');
        if (!courseSelect || !institutionId) {
            if (courseSelect) {
                courseSelect.innerHTML = '<option value="">Select Course</option>';
            }
            return;
        }
        
        try {
            const response = await fetch(`/api/colleges/courses/${institutionId}`);
            const data = await response.json();
            const courses = data.courses || [];
            
            courseSelect.innerHTML = '<option value="">Select Course</option>';
            
            courses.forEach(course => {
                const option = document.createElement('option');
                option.value = course;
                option.textContent = course;
                courseSelect.appendChild(option);
            });
            
        } catch (error) {
            console.error('Error loading courses:', error);
            courseSelect.innerHTML = '<option value="">Courses unavailable</option>';
        }
    }
    
    // College search functionality
    async searchColleges(query) {
        try {
            const response = await fetch('/api/colleges/search', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ query: query })
            });
            
            const data = await response.json();
            return data.colleges || [];
            
        } catch (error) {
            console.error('Error searching colleges:', error);
            return [];
        }
    }
    
    // Enhanced credential issuance with college validation
    async issueCredential() {
        if (this.isLoading) return;
        
        const form = document.getElementById('issueCredentialForm');
        const formData = new FormData(form);
        
        const institutionId = formData.get('institutionId');
        
        // Validate institution exists
        if (institutionId) {
            try {
                const response = await fetch(`/api/colleges/${institutionId}`);
                if (!response.ok) {
                    this.showNotification('Selected institution not found in database', 'error');
                    return;
                }
            } catch (error) {
                this.showNotification('Unable to verify institution', 'error');
                return;
            }
        }
        
        try {
            this.showLoading();
            this.showNotification('Issuing credential...', 'info');
            
            const response = await fetch('/api/credentials/issue', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    student_name: formData.get('studentName'),
                    student_email: formData.get('studentEmail'),
                    credential_title: formData.get('credentialTitle'),
                    credential_type: formData.get('credentialType'),
                    institution_id: institutionId,
                    course: formData.get('credentialCourse') || formData.get('credentialTitle'),
                    grade: formData.get('grade') || 'A'
                })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showNotification('Credential issued successfully!', 'success');
                this.clearCache('credentials');
                this.clearCache('dashboard');
                form.reset();
                
                // Reset course dropdown
                const courseSelect = document.getElementById('credentialCourse');
                if (courseSelect) {
                    courseSelect.innerHTML = '<option value="">Select Course</option>';
                }
                
                // Show QR code if available
                if (result.qr_code) {
                    this.showQRCode(result.qr_code);
                }
            } else {
                this.showNotification(result.error || 'Failed to issue credential', 'error');
            }
            
        } catch (error) {
            console.error('Issue credential error:', error);
            this.showNotification('Error issuing credential', 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    initializeMinimalVFX() {
        // Only essential visual effects for performance
        this.addClickRipples();
        this.addHoverEffects();
    }
    
    addClickRipples() {
        document.addEventListener('click', (e) => {
            if (e.target.matches('button, .btn, .tab-btn')) {
                const ripple = document.createElement('span');
                ripple.className = 'ripple';
                
                const rect = e.target.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.style.width = ripple.style.height = size + 'px';
                ripple.style.left = x + 'px';
                ripple.style.top = y + 'px';
                
                e.target.appendChild(ripple);
                
                setTimeout(() => ripple.remove(), 600);
            }
        });
    }
    
    addHoverEffects() {
        const cards = document.querySelectorAll('.stat-card, .credential-card, .institution-card');
        cards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-2px)';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0)';
            });
        });
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.validator = new OptimizedAcademicValidator();
});

// Utility functions
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.style.display = 'none';
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.style.display = 'flex';
}
