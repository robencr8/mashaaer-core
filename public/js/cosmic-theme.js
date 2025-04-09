/**
 * cosmic-theme.js - خلفية كونية تفاعلية لتطبيق مشاعر
 * تم تطويره بواسطة فريق مشاعر
 * الإصدار 1.0.1 (مُحدَّث للتفاعلية والدمج)
 */

class CosmicBackground {
    /**
     * إنشاء خلفية كونية تفاعلية
     * @param {Object} options - خيارات تكوين الخلفية الكونية
     */
    constructor(options = {}) {
        // الإعدادات الافتراضية
        this.settings = {
            container: options.container || document.body,
            starsBrightness: options.starsBrightness || 0.7,
            nebulaIntensity: options.nebulaIntensity || 0.8,
            animationSpeed: options.animationSpeed || 0.5,
            reduceMotion: options.reduceMotion !== undefined ? options.reduceMotion : true,
            showControls: options.showControls !== undefined ? options.showControls : false,
            autoResize: options.autoResize !== undefined ? options.autoResize : true,
            onReady: options.onReady || null,
            theme: options.theme || 'blue-purple', // blue-purple, green-blue, orange-red
            zIndex: options.zIndex || -1,
            enableAudio: options.enableAudio !== undefined ? options.enableAudio : true, // تمكين الصوت
            welcomeSound: options.welcomeSound || 'welcome.mp3', // مسار صوت الترحيب
            clickSound: options.clickSound || 'click.mp3', // مسار صوت النقر
            emotionChangeSpeed: options.emotionChangeSpeed || 2000 // سرعة تغيير المشاعر (مللي ثانية)
        };

        // حالة الخلفية
        this.state = {
            isPaused: false,
            mouseX: 0,
            mouseY: 0,
            touchActive: false,
            showNebula: true,
            showStars: true,
            showDust: true,
            isInitialized: false,
            currentEmotion: 'neutral', // المشاعر الحالية
            emotionTransitioning: false // هل يتم الانتقال بين المشاعر؟
        };

        // عناصر DOM
        this.container = null;
        this.canvasContainer = null;
        this.starsCanvas = null;
        this.nebulaCanvas = null;
        this.dustCanvas = null;
        this.meteorsCanvas = null;
        this.interactionCanvas = null;
        this.controlsContainer = null;
        this.audioPlayer = null; // مشغل الصوت

        // سياقات الرسم
        this.starsCtx = null;
        this.nebulaCtx = null;
        this.dustCtx = null;
        this.meteorsCtx = null;
        this.interactionCtx = null;

        // المصفوفات الكونية
        this.stars = [];
        this.nebulaPoints = [];
        this.dustParticles = [];
        this.meteors = [];
        this.nebulaTime = 0;

        // تهيئة الخلفية
        this._initialize();
    }

    /**
     * تهيئة الخلفية الكونية
     * @private
     */
    _initialize() {
        // تحديد الحاوية
        if (typeof this.settings.container === 'string') {
            this.container = document.querySelector(this.settings.container);
        } else {
            this.container = this.settings.container;
        }

        // التحقق من وجود الحاوية
        if (!this.container) {
            console.error('لم يتم العثور على حاوية الخلفية الكونية');
            return;
        }

        // إنشاء حاوية الـ canvas
        this.canvasContainer = document.createElement('div');
        this.canvasContainer.className = 'cosmic-background';
        this.canvasContainer.style.position = 'absolute';
        this.canvasContainer.style.top = '0';
        this.canvasContainer.style.left = '0';
        this.canvasContainer.style.width = '100%';
        this.canvasContainer.style.height = '100%';
        this.canvasContainer.style.overflow = 'hidden';
        this.canvasContainer.style.zIndex = this.settings.zIndex.toString();

        // إضافة حاوية الـ canvas إلى الحاوية الرئيسية
        if (this.container === document.body) {
            this.canvasContainer.style.position = 'fixed';
        }
        
        // التأكد من أن الحاوية الرئيسية لديها position: relative إذا لم تكن بالفعل
        const containerPosition = window.getComputedStyle(this.container).position;
        if (containerPosition === 'static') {
            this.container.style.position = 'relative';
        }
        
        this.container.appendChild(this.canvasContainer);

        // إنشاء عناصر canvas
        this.starsCanvas = this._createCanvas('cosmic-stars-canvas');
        this.nebulaCanvas = this._createCanvas('cosmic-nebula-canvas');
        this.dustCanvas = this._createCanvas('cosmic-dust-canvas');
        this.meteorsCanvas = this._createCanvas('cosmic-meteors-canvas');
        this.interactionCanvas = this._createCanvas('cosmic-interaction-canvas');

        // الحصول على سياقات الرسم
        this.starsCtx = this.starsCanvas.getContext('2d');
        this.nebulaCtx = this.nebulaCanvas.getContext('2d');
        this.dustCtx = this.dustCanvas.getContext('2d');
        this.meteorsCtx = this.meteorsCanvas.getContext('2d');
        this.interactionCtx = this.interactionCanvas.getContext('2d');

        // إضافة عناصر التحكم إذا كان مطلوباً
        if (this.settings.showControls) {
            this._createControls();
        }

        // إعداد الصوت
        if (this.settings.enableAudio) {
            this._setupAudio();
        }

        // إضافة مستمعي الأحداث
        this._setupEventListeners();

        // ضبط أحجام canvas
        this._resizeCanvases();

        // تهيئة العناصر الكونية
        this._initializeCosmicElements();

        // تعيين حالة التهيئة
        this.state.isInitialized = true;

        // استدعاء دالة الاستعداد إذا كانت موجودة
        if (typeof this.settings.onReady === 'function') {
            this.settings.onReady(this);
        }
    }

    /**
     * إنشاء عنصر canvas
     * @param {string} className - اسم الفئة للـ canvas
     * @returns {HTMLCanvasElement} - عنصر canvas جديد
     * @private
     */
    _createCanvas(className) {
        const canvas = document.createElement('canvas');
        canvas.className = className;
        canvas.style.position = 'absolute';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        this.canvasContainer.appendChild(canvas);
        return canvas;
    }

    /**
     * إنشاء عناصر التحكم
     * @private
     */
    _createControls() {
        this.controlsContainer = document.createElement('div');
        this.controlsContainer.className = 'cosmic-controls';
        this.controlsContainer.style.position = 'absolute';
        this.controlsContainer.style.top = '10px';
        this.controlsContainer.style.right = '10px';
        this.controlsContainer.style.zIndex = (parseInt(this.settings.zIndex) + 1).toString();
        this.controlsContainer.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        this.controlsContainer.style.padding = '10px';
        this.controlsContainer.style.borderRadius = '5px';
        this.controlsContainer.style.color = 'white';
        this.controlsContainer.style.fontSize = '12px';
        this.controlsContainer.style.display = 'flex';
        this.controlsContainer.style.flexDirection = 'column';
        this.controlsContainer.style.gap = '5px';
        this.controlsContainer.style.direction = 'rtl';
        this.controlsContainer.style.textAlign = 'right';

        // إنشاء عناصر التحكم
        const controls = [
            {
                type: 'range',
                label: 'سطوع النجوم',
                id: 'cosmic-stars-brightness',
                min: 0,
                max: 100,
                value: this.settings.starsBrightness * 100,
                onChange: (value) => {
                    this.settings.starsBrightness = value / 100;
                    this._drawStars();
                }
            },
            {
                type: 'range',
                label: 'كثافة السديم',
                id: 'cosmic-nebula-intensity',
                min: 0,
                max: 100,
                value: this.settings.nebulaIntensity * 100,
                onChange: (value) => {
                    this.settings.nebulaIntensity = value / 100;
                }
            },
            {
                type: 'range',
                label: 'سرعة الحركة',
                id: 'cosmic-animation-speed',
                min: 0,
                max: 100,
                value: this.settings.animationSpeed * 100,
                onChange: (value) => {
                    this.settings.animationSpeed = value / 100;
                }
            },
            {
                type: 'checkbox',
                label: 'تقليل الحركة',
                id: 'cosmic-reduce-motion',
                checked: this.settings.reduceMotion,
                onChange: (checked) => {
                    this.settings.reduceMotion = checked;
                }
            }
        ];

        // إضافة عناصر التحكم إلى الحاوية
        controls.forEach(control => {
            const controlContainer = document.createElement('div');
            controlContainer.style.display = 'flex';
            controlContainer.style.alignItems = 'center';
            controlContainer.style.gap = '5px';

            const label = document.createElement('label');
            label.textContent = control.label;
            label.style.flexGrow = '1';
            label.htmlFor = control.id;

            const input = document.createElement('input');
            input.type = control.type;
            input.id = control.id;

            if (control.type === 'range') {
                input.min = control.min;
                input.max = control.max;
                input.value = control.value;
                input.style.width = '80px';
                input.addEventListener('input', () => {
                    control.onChange(parseFloat(input.value));
                });
            } else if (control.type === 'checkbox') {
                input.checked = control.checked;
                input.addEventListener('change', () => {
                    control.onChange(input.checked);
                });
            }

            controlContainer.appendChild(label);
            controlContainer.appendChild(input);
            this.controlsContainer.appendChild(controlContainer);
        });

        this.canvasContainer.appendChild(this.controlsContainer);
    }

    /**
     * إعداد الصوت
     * @private
     */
    _setupAudio() {
        this.audioPlayer = document.createElement('audio');
        this.audioPlayer.id = 'cosmic-audio-player';
        // تعطيل الصوت مؤقتًا حتى نتأكد من وجود الملفات الصوتية
        // this.audioPlayer.src = this.settings.welcomeSound;
        this.audioPlayer.volume = 0.5;
        this.audioPlayer.loop = true;
        this.audioPlayer.style.display = 'none'; // إخفاء المشغل
        this.canvasContainer.appendChild(this.audioPlayer);

        // تشغيل صوت الترحيب عند التهيئة - معطل مؤقتًا
        /*
        this.audioPlayer.play().catch(error => {
            console.warn('لم يتم تشغيل صوت الترحيب تلقائياً:', error);
        });
        */
    }

    /**
     * إعداد مستمعي الأحداث
     * @private
     */
    _setupEventListeners() {
        // مستمع تغيير حجم النافذة
        if (this.settings.autoResize) {
            window.addEventListener('resize', this._resizeCanvases.bind(this));
        }

        // مستمعي حركة الماوس واللمس
        this.interactionCanvas.addEventListener('mousemove', (e) => {
            const rect = this.interactionCanvas.getBoundingClientRect();
            this.state.mouseX = e.clientX - rect.left;
            this.state.mouseY = e.clientY - rect.top;
        });

        this.interactionCanvas.addEventListener('touchstart', (e) => {
            this.state.touchActive = true;
            if (e.touches.length > 0) {
                const rect = this.interactionCanvas.getBoundingClientRect();
                this.state.mouseX = e.touches[0].clientX - rect.left;
                this.state.mouseY = e.touches[0].clientY - rect.top;
            }
        });

        this.interactionCanvas.addEventListener('touchmove', (e) => {
            if (e.touches.length > 0) {
                const rect = this.interactionCanvas.getBoundingClientRect();
                this.state.mouseX = e.touches[0].clientX - rect.left;
                this.state.mouseY = e.touches[0].clientY - rect.top;
            }
        });

        this.interactionCanvas.addEventListener('touchend', () => {
            this.state.touchActive = false;
        });

        // مستمع مفتاح ESC لإيقاف الحركة
        window.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.togglePause();
            }
        });
    }

    /**
     * ضبط أحجام canvas
     * @private
     */
    _resizeCanvases() {
        const width = this.canvasContainer.clientWidth;
        const height = this.canvasContainer.clientHeight;
        
        const canvases = [
            this.starsCanvas,
            this.nebulaCanvas,
            this.dustCanvas,
            this.meteorsCanvas,
            this.interactionCanvas
        ];
        
        canvases.forEach(canvas => {
            if (canvas) {
                canvas.width = width;
                canvas.height = height;
            }
        });
        
        // إعادة توليد نقاط السديم
        if (this.state.isInitialized) {
            this._generateNebulaPoints();
            this._drawStars();
        }
    }

    /**
     * تهيئة العناصر الكونية
     * @private
     */
    _initializeCosmicElements() {
        // إنشاء النجوم
        for (let i = 0; i < 1500; i++) {
            this.stars.push(new this.Star(this));
        }
        
        // إنشاء جزيئات الغبار الكوني
        for (let i = 0; i < 300; i++) {
            this.dustParticles.push(new this.DustParticle(this));
        }
        
        // إنشاء الشهب
        for (let i = 0; i < 5; i++) {
            this.meteors.push(new this.Meteor(this));
        }
        
        // إنشاء نقاط السديم
        this._generateNebulaPoints();
        
        // بدء حلقة الرسم
        this._startAnimationLoop();
    }

    /**
     * توليد نقاط السديم
     * @private
     */
    _generateNebulaPoints() {
        this.nebulaPoints = [];
        const centerX = this.nebulaCanvas.width / 2;
        const centerY = this.nebulaCanvas.height / 2;
        const radius = Math.min(this.nebulaCanvas.width, this.nebulaCanvas.height) * 0.3;
        
        // إنشاء نقاط عشوائية حول المركز
        for (let i = 0; i < 8; i++) {
            const angle = (i / 8) * Math.PI * 2;
            const distance = radius * (0.8 + Math.random() * 0.4);
            const x = centerX + Math.cos(angle) * distance;
            const y = centerY + Math.sin(angle) * distance;
            
            this.nebulaPoints.push({
                x, y,
                originalX: x,
                originalY: y,
                angle,
                distance
            });
        }
    }

    /**
     * بدء حلقة الرسم
     * @private
     */
    _startAnimationLoop() {
        let lastDrawTime = 0;
        const drawInterval = 1000 / 60; // 60 إطار في الثانية
        
        const animate = (timestamp) => {
            // حساب الوقت المنقضي منذ آخر رسم
            const elapsed = timestamp - lastDrawTime;
            
            // تحديث العناصر في كل إطار
            if (!this.state.isPaused) {
                this.stars.forEach(star => star.update(timestamp));
                this.dustParticles.forEach(particle => particle.update());
                this.meteors.forEach(meteor => meteor.update());
            }
            
            // رسم العناصر فقط إذا مر وقت كافٍ
            if (elapsed >= drawInterval) {
                this._drawStars();
                this._drawNebula(timestamp);
                this._drawDust();
                this._drawMeteors();
                this._drawInteraction(timestamp);
                
                lastDrawTime = timestamp;
            }
            
            // استمرار الحلقة
            requestAnimationFrame(animate);
        };
        
        requestAnimationFrame(animate);
    }

    /**
     * رسم النجوم
     * @private
     */
    _drawStars() {
        if (!this.starsCtx) return;
        
        this.starsCtx.clearRect(0, 0, this.starsCanvas.width, this.starsCanvas.height);
        
        if (this.state.showStars) {
            this.stars.forEach(star => {
                star.draw(this.starsCtx);
            });
        }
    }

    /**
     * رسم السديم
     * @param {number} time - الوقت الحالي
     * @private
     */
    _drawNebula(time) {
        if (!this.nebulaCtx || !this.state.showNebula) {
            if (this.nebulaCtx) {
                this.nebulaCtx.clearRect(0, 0, this.nebulaCanvas.width, this.nebulaCanvas.height);
            }
            return;
        }
        
        this.nebulaCtx.clearRect(0, 0, this.nebulaCanvas.width, this.nebulaCanvas.height);
        
        // تحديث نقاط السديم
        if (!this.state.isPaused) {
            this.nebulaTime += 0.001 * this.settings.animationSpeed * (this.settings.reduceMotion ? 0.3 : 1);
            
            this.nebulaPoints.forEach((point, index) => {
                const wobble = Math.sin(this.nebulaTime + index) * 20;
                point.x = point.originalX + Math.cos(point.angle + this.nebulaTime) * wobble;
                point.y = point.originalY + Math.sin(point.angle + this.nebulaTime) * wobble;
            });
        }
        
        const centerX = this.nebulaCanvas.width / 2;
        const centerY = this.nebulaCanvas.height / 2;
        
        // تحديد ألوان السديم بناءً على السمة
        let colors;
        switch (this.settings.theme) {
            case 'green-blue':
                colors = {
                    center: `rgba(255, 255, 255, ${0.8 * this.settings.nebulaIntensity})`,
                    inner: `rgba(0, 200, 100, ${0.6 * this.settings.nebulaIntensity})`,
                    middle: `rgba(0, 100, 150, ${0.5 * this.settings.nebulaIntensity})`,
                    outer1: `rgba(0, 150, 200, ${0.4 * this.settings.nebulaIntensity})`,
                    outer2: `rgba(0, 50, 100, ${0.3 * this.settings.nebulaIntensity})`
                };
                break;
            case 'orange-red':
                colors = {
                    center: `rgba(255, 255, 255, ${0.8 * this.settings.nebulaIntensity})`,
                    inner: `rgba(255, 200, 0, ${0.6 * this.settings.nebulaIntensity})`,
                    middle: `rgba(255, 100, 0, ${0.5 * this.settings.nebulaIntensity})`,
                    outer1: `rgba(200, 50, 0, ${0.4 * this.settings.nebulaIntensity})`,
                    outer2: `rgba(100, 0, 0, ${0.3 * this.settings.nebulaIntensity})`
                };
                break;
            default: // blue-purple
                colors = {
                    center: `rgba(255, 255, 255, ${0.8 * this.settings.nebulaIntensity})`,
                    inner: `rgba(74, 137, 220, ${0.6 * this.settings.nebulaIntensity})`,
                    middle: `rgba(28, 60, 120, ${0.5 * this.settings.nebulaIntensity})`,
                    outer1: `rgba(255, 105, 180, ${0.4 * this.settings.nebulaIntensity})`,
                    outer2: `rgba(128, 0, 128, ${0.3 * this.settings.nebulaIntensity})`
                };
        }
        
        // طبقة 1: الهالة الخارجية
        const outerGradient = this.nebulaCtx.createRadialGradient(
            centerX, centerY, 0,
            centerX, centerY, Math.min(this.nebulaCanvas.width, this.nebulaCanvas.height) * 0.5
        );
        
        outerGradient.addColorStop(0, `rgba(28, 60, 120, 0)`);
        outerGradient.addColorStop(0.5, `rgba(28, 60, 120, ${0.1 * this.settings.nebulaIntensity})`);
        outerGradient.addColorStop(0.8, `rgba(28, 60, 120, ${0.05 * this.settings.nebulaIntensity})`);
        outerGradient.addColorStop(1, `rgba(0, 0, 0, 0)`);
        
        this.nebulaCtx.beginPath();
        this.nebulaCtx.arc(centerX, centerY, Math.min(this.nebulaCanvas.width, this.nebulaCanvas.height) * 0.5, 0, Math.PI * 2);
        this.nebulaCtx.fillStyle = outerGradient;
        this.nebulaCtx.fill();
        
        // طبقة 2: السديم الرئيسي
        const mainGradient = this.nebulaCtx.createRadialGradient(
            centerX, centerY, 0,
            centerX, centerY, Math.min(this.nebulaCanvas.width, this.nebulaCanvas.height) * 0.4
        );
        
        mainGradient.addColorStop(0, `rgba(255, 255, 255, ${0.8 * this.settings.nebulaIntensity})`);
        mainGradient.addColorStop(0.2, `rgba(74, 137, 220, ${0.6 * this.settings.nebulaIntensity})`);
        mainGradient.addColorStop(0.4, `rgba(28, 60, 120, ${0.5 * this.settings.nebulaIntensity})`);
        mainGradient.addColorStop(0.6, `rgba(255, 105, 180, ${0.4 * this.settings.nebulaIntensity})`);
        mainGradient.addColorStop(0.8, `rgba(128, 0, 128, ${0.3 * this.settings.nebulaIntensity})`);
        mainGradient.addColorStop(1, `rgba(0, 0, 0, 0)`);
        
        // رسم السديم باستخدام منحنى بيزيه
        this.nebulaCtx.globalCompositeOperation = 'source-over';
        this.nebulaCtx.beginPath();
        this.nebulaCtx.moveTo(this.nebulaPoints[0].x, this.nebulaPoints[0].y);
        
        for (let i = 0; i < this.nebulaPoints.length; i++) {
            const currentPoint = this.nebulaPoints[i];
            const nextPoint = this.nebulaPoints[(i + 1) % this.nebulaPoints.length];
            
            const controlX = (currentPoint.x + nextPoint.x) / 2;
            const controlY = (currentPoint.y + nextPoint.y) / 2;
            
            this.nebulaCtx.quadraticCurveTo(
                currentPoint.x, currentPoint.y,
                controlX, controlY
            );
        }
        
        this.nebulaCtx.closePath();
        this.nebulaCtx.fillStyle = mainGradient;
        this.nebulaCtx.fill();
        
        // طبقة 3: إضافة تفاصيل داخلية للسديم
        this.nebulaCtx.globalCompositeOperation = 'screen';
        
        // إضافة خطوط مضيئة داخل السديم
        for (let i = 0; i < 5; i++) {
            const angle = Math.random() * Math.PI * 2;
            const length = Math.random() * 100 + 50;
            const startX = centerX + Math.cos(angle) * 20;
            const startY = centerY + Math.sin(angle) * 20;
            const endX = startX + Math.cos(angle) * length;
            const endY = startY + Math.sin(angle) * length;
            
            const glowGradient = this.nebulaCtx.createLinearGradient(startX, startY, endX, endY);
            glowGradient.addColorStop(0, `rgba(255, 255, 255, ${0.7 * this.settings.nebulaIntensity})`);
            glowGradient.addColorStop(0.5, `rgba(74, 137, 220, ${0.5 * this.settings.nebulaIntensity})`);
            glowGradient.addColorStop(1, `rgba(0, 0, 0, 0)`);
            
            this.nebulaCtx.beginPath();
            this.nebulaCtx.strokeStyle = glowGradient;
            this.nebulaCtx.lineWidth = Math.random() * 5 + 2;
            this.nebulaCtx.moveTo(startX, startY);
            this.nebulaCtx.lineTo(endX, endY);
            this.nebulaCtx.stroke();
        }
        
        // طبقة 4: إضافة توهج للسديم
        this.nebulaCtx.filter = 'blur(30px)';
        this.nebulaCtx.beginPath();
        this.nebulaCtx.arc(centerX, centerY, Math.min(this.nebulaCanvas.width, this.nebulaCanvas.height) * 0.2, 0, Math.PI * 2);
        this.nebulaCtx.fillStyle = mainGradient;
        this.nebulaCtx.fill();
        
        // طبقة 5: إضافة نجوم ساطعة داخل السديم
        this.nebulaCtx.filter = 'none';
        for (let i = 0; i < 8; i++) {
            const angle = Math.random() * Math.PI * 2;
            const distance = Math.random() * 150;
            const x = centerX + Math.cos(angle) * distance;
            const y = centerY + Math.sin(angle) * distance;
            const size = Math.random() * 3 + 1;
            
            // رسم النجمة
            this.nebulaCtx.beginPath();
            this.nebulaCtx.arc(x, y, size, 0, Math.PI * 2);
            this.nebulaCtx.fillStyle = `rgba(255, 255, 255, ${0.8 * this.settings.nebulaIntensity})`;
            this.nebulaCtx.fill();
            
            // إضافة توهج حول النجمة
            this.nebulaCtx.beginPath();
            this.nebulaCtx.arc(x, y, size * 3, 0, Math.PI * 2);
            const starGlow = this.nebulaCtx.createRadialGradient(x, y, 0, x, y, size * 3);
            starGlow.addColorStop(0, `rgba(255, 255, 255, ${0.5 * this.settings.nebulaIntensity})`);
            starGlow.addColorStop(1, `rgba(255, 255, 255, 0)`);
            this.nebulaCtx.fillStyle = starGlow;
            this.nebulaCtx.fill();
        }
        
        // إعادة تعيين globalCompositeOperation
        this.nebulaCtx.globalCompositeOperation = 'source-over';
    }

    /**
     * رسم جزيئات الغبار الكوني
     * @private
     */
    _drawDust() {
        if (!this.dustCtx || !this.state.showDust) {
            if (this.dustCtx) {
                this.dustCtx.clearRect(0, 0, this.dustCanvas.width, this.dustCanvas.height);
            }
            return;
        }
        
        this.dustCtx.clearRect(0, 0, this.dustCanvas.width, this.dustCanvas.height);
        
        this.dustParticles.forEach(particle => {
            particle.draw(this.dustCtx);
        });
    }

    /**
     * رسم الشهب
     * @private
     */
    _drawMeteors() {
        if (!this.meteorsCtx) return;
        
        this.meteorsCtx.clearRect(0, 0, this.meteorsCanvas.width, this.meteorsCanvas.height);
        
        this.meteors.forEach(meteor => {
            meteor.draw(this.meteorsCtx);
        });
    }

    /**
     * رسم تأثيرات التفاعل
     * @param {number} time - الوقت الحالي
     * @private
     */
    _drawInteraction(time) {
        if (!this.interactionCtx) return;
        
        this.interactionCtx.clearRect(0, 0, this.interactionCanvas.width, this.interactionCanvas.height);
        
        // رسم تأثير التفاعل فقط إذا كان المؤشر أو اللمس نشطاً
        if (this.state.touchActive || (this.state.mouseX !== 0 && this.state.mouseY !== 0)) {
            this._drawMouseInteraction(time);
        }
    }

    /**
     * رسم تأثير تفاعل الماوس
     * @param {number} time - الوقت الحالي
     * @private
     */
    _drawMouseInteraction(time) {
        const ctx = this.interactionCtx;
        const pulseSpeed = 0.0005;
        const pulseSize = 20 + Math.sin(time * pulseSpeed) * 10;
        const pulseOpacity = 0.3 + Math.cos(time * pulseSpeed) * 0.2;
        
        ctx.beginPath();
        const gradient = ctx.createRadialGradient(
            this.state.mouseX, this.state.mouseY, 0,
            this.state.mouseX, this.state.mouseY, pulseSize
        );
        
        gradient.addColorStop(0, `rgba(255, 255, 255, ${pulseOpacity})`);
        gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
        
        ctx.fillStyle = gradient;
        ctx.arc(this.state.mouseX, this.state.mouseY, pulseSize, 0, Math.PI * 2);
        ctx.fill();
    }

    /**
     * فئة النجوم
     */
    Star = class {
        constructor(cosmic) {
            this.cosmic = cosmic;
            this.reset();
        }
        
        reset() {
            this.x = Math.random() * this.cosmic.starsCanvas.width;
            this.y = Math.random() * this.cosmic.starsCanvas.height;
            this.size = Math.random() * 2 + 0.5;
            this.brightness = Math.random() * 0.5 + 0.5;
            this.twinkleSpeed = Math.random() * 0.01 + 0.005;
            this.twinklePhase = Math.random() * Math.PI * 2;
            this.color = '#ffffff';
        }
        
        update(timestamp) {
            if (this.cosmic.state.isPaused) return;
            
            // تومض النجوم
            this.twinklePhase += this.twinkleSpeed * this.cosmic.settings.animationSpeed;
            this.brightness = 0.5 + Math.sin(this.twinklePhase) * 0.5;
            
            // تتحرك النجوم قليلاً
            if (!this.cosmic.settings.reduceMotion) {
                this.y += 0.05 * this.cosmic.settings.animationSpeed;
                
                // إعادة ضبط النجمة عندما تخرج عن الشاشة
                if (this.y > this.cosmic.starsCanvas.height) {
                    this.y = 0;
                    this.x = Math.random() * this.cosmic.starsCanvas.width;
                }
            }
        }
        
        draw(ctx) {
            const opacity = this.brightness * this.cosmic.settings.starsBrightness;
            const size = this.size * (0.8 + this.brightness * 0.4);
            
            // رسم النجمة
            ctx.beginPath();
            ctx.arc(this.x, this.y, size, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(255, 255, 255, ${opacity})`;
            ctx.fill();
            
            // رسم التوهج حول النجمة الأكبر
            if (this.size > 1.5) {
                ctx.beginPath();
                ctx.arc(this.x, this.y, size * 3, 0, Math.PI * 2);
                const glow = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, size * 3);
                glow.addColorStop(0, `rgba(255, 255, 255, ${opacity * 0.5})`);
                glow.addColorStop(1, 'rgba(255, 255, 255, 0)');
                ctx.fillStyle = glow;
                ctx.fill();
            }
        }
    };

    /**
     * فئة جزيئات الغبار الكوني
     */
    DustParticle = class {
        constructor(cosmic) {
            this.cosmic = cosmic;
            this.reset();
        }
        
        reset() {
            this.x = Math.random() * this.cosmic.dustCanvas.width;
            this.y = Math.random() * this.cosmic.dustCanvas.height;
            this.size = Math.random() * 0.6 + 0.2;
            this.speedX = (Math.random() - 0.5) * 0.1;
            this.speedY = (Math.random() - 0.5) * 0.1;
            this.opacity = Math.random() * 0.3 + 0.2;
        }
        
        update() {
            if (this.cosmic.state.isPaused) return;
            
            // تحريك جزيئات الغبار
            this.x += this.speedX * this.cosmic.settings.animationSpeed * (this.cosmic.settings.reduceMotion ? 0.3 : 1);
            this.y += this.speedY * this.cosmic.settings.animationSpeed * (this.cosmic.settings.reduceMotion ? 0.3 : 1);
            
            // إعادة ضبط الجزيء عندما يخرج عن الشاشة
            if (this.x < 0 || this.x > this.cosmic.dustCanvas.width || this.y < 0 || this.y > this.cosmic.dustCanvas.height) {
                this.reset();
            }
        }
        
        draw(ctx) {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(255, 255, 255, ${this.opacity * this.cosmic.settings.nebulaIntensity})`;
            ctx.fill();
        }
    };

    /**
     * فئة الشهب
     */
    Meteor = class {
        constructor(cosmic) {
            this.cosmic = cosmic;
            this.reset();
            this.visible = false; // يبدأ غير مرئي
            this.cooldown = Math.floor(Math.random() * 500) + 100; // تأخير عشوائي
        }
        
        reset() {
            this.startX = Math.random() * this.cosmic.meteorsCanvas.width;
            this.startY = 0;
            this.endX = this.startX + (Math.random() - 0.5) * 300;
            this.endY = this.cosmic.meteorsCanvas.height;
            this.progress = 0;
            this.speed = Math.random() * 0.01 + 0.005;
            this.width = Math.random() * 2 + 1;
            this.length = Math.random() * 80 + 50;
        }
        
        update() {
            if (this.cosmic.state.isPaused) return;
            
            if (!this.visible) {
                this.cooldown--;
                if (this.cooldown <= 0) {
                    this.visible = true;
                }
                return;
            }
            
            this.progress += this.speed * this.cosmic.settings.animationSpeed * (this.cosmic.settings.reduceMotion ? 0.3 : 1);
            
            if (this.progress >= 1) {
                this.reset();
                this.visible = false;
                this.cooldown = Math.floor(Math.random() * 500) + 1000;
            }
        }
        
        draw(ctx) {
            if (!this.visible) return;
            
            const x = this.startX + (this.endX - this.startX) * this.progress;
            const y = this.startY + (this.endY - this.startY) * this.progress;
            
            // حساب زاوية الشهاب
            const angle = Math.atan2(this.endY - this.startY, this.endX - this.startX);
            
            // رسم ذيل الشهاب
            ctx.save();
            ctx.translate(x, y);
            ctx.rotate(angle);
            
            const gradient = ctx.createLinearGradient(0, 0, -this.length, 0);
            gradient.addColorStop(0, 'rgba(255, 255, 255, 0.8)');
            gradient.addColorStop(0.2, 'rgba(255, 255, 255, 0.3)');
            gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
            
            ctx.beginPath();
            ctx.moveTo(0, 0);
            ctx.lineTo(-this.length, this.width);
            ctx.lineTo(-this.length, -this.width);
            ctx.closePath();
            ctx.fillStyle = gradient;
            ctx.fill();
            
            // رسم رأس الشهاب
            ctx.beginPath();
            ctx.arc(0, 0, this.width * 2, 0, Math.PI * 2);
            ctx.fillStyle = 'white';
            ctx.fill();
            
            ctx.restore();
        }
    };

    /**
     * تغيير السمة الكونية
     * @param {string} theme - السمة المطلوبة ('blue-purple', 'green-blue', 'orange-red')
     */
    setTheme(theme) {
        if (['blue-purple', 'green-blue', 'orange-red'].includes(theme)) {
            this.settings.theme = theme;
        } else {
            console.warn(`السمة غير صالحة: ${theme}. استخدام 'blue-purple' كسمة افتراضية.`);
            this.settings.theme = 'blue-purple';
        }
    }

    /**
     * تغيير مشاعر الخلفية الكونية
     * @param {string} emotion - المشاعر المطلوبة ('happy', 'sad', 'angry', 'neutral', etc.)
     */
    setEmotion(emotion) {
        if (this.state.emotionTransitioning) return;
        
        this.state.emotionTransitioning = true;
        this.state.currentEmotion = emotion;
        
        // تعيين السمة المناسبة للمشاعر
        switch (emotion) {
            case 'happy':
                this.settings.theme = 'green-blue'; // سعيد - ألوان زرقاء وخضراء
                this.settings.starsBrightness = 0.8;
                this.settings.nebulaIntensity = 0.9;
                this.settings.animationSpeed = 0.8;
                break;
            case 'sad':
                this.settings.theme = 'blue-purple'; // حزين - ألوان زرقاء وأرجوانية
                this.settings.starsBrightness = 0.5;
                this.settings.nebulaIntensity = 0.5;
                this.settings.animationSpeed = 0.3;
                break;
            case 'angry':
                this.settings.theme = 'orange-red'; // غاضب - ألوان برتقالية وحمراء
                this.settings.starsBrightness = 0.9;
                this.settings.nebulaIntensity = 1.0;
                this.settings.animationSpeed = 1.0;
                break;
            default: // neutral or any other emotion
                this.settings.theme = 'blue-purple'; // محايد - ألوان زرقاء وأرجوانية
                this.settings.starsBrightness = 0.7;
                this.settings.nebulaIntensity = 0.8;
                this.settings.animationSpeed = 0.5;
        }
        
        // السماح بإعادة تغيير المشاعر بعد فترة
        setTimeout(() => {
            this.state.emotionTransitioning = false;
        }, this.settings.emotionChangeSpeed);
    }

    /**
     * إيقاف/تشغيل الخلفية الكونية
     */
    togglePause() {
        this.state.isPaused = !this.state.isPaused;
        return this.state.isPaused;
    }

    /**
     * تغيير عرض/إخفاء السديم
     * @param {boolean} show - عرض السديم
     */
    toggleNebula(show) {
        if (show !== undefined) {
            this.state.showNebula = show;
        } else {
            this.state.showNebula = !this.state.showNebula;
        }
        return this.state.showNebula;
    }

    /**
     * تغيير عرض/إخفاء النجوم
     * @param {boolean} show - عرض النجوم
     */
    toggleStars(show) {
        if (show !== undefined) {
            this.state.showStars = show;
        } else {
            this.state.showStars = !this.state.showStars;
        }
        
        if (!this.state.showStars && this.starsCtx) {
            this.starsCtx.clearRect(0, 0, this.starsCanvas.width, this.starsCanvas.height);
        }
        
        return this.state.showStars;
    }

    /**
     * تغيير عرض/إخفاء الغبار الكوني
     * @param {boolean} show - عرض الغبار الكوني
     */
    toggleDust(show) {
        if (show !== undefined) {
            this.state.showDust = show;
        } else {
            this.state.showDust = !this.state.showDust;
        }
        
        if (!this.state.showDust && this.dustCtx) {
            this.dustCtx.clearRect(0, 0, this.dustCanvas.width, this.dustCanvas.height);
        }
        
        return this.state.showDust;
    }

    /**
     * تشغيل صوت
     * @param {string} sound - مسار الصوت
     * @param {boolean} loop - تكرار الصوت
     * @param {number} volume - مستوى الصوت (0.0 - 1.0)
     */
    playSound(sound, loop = false, volume = 0.5) {
        if (!this.settings.enableAudio || !this.audioPlayer) return;
        
        this.audioPlayer.src = sound;
        this.audioPlayer.loop = loop;
        this.audioPlayer.volume = volume;
        
        this.audioPlayer.play().catch(error => {
            console.warn('لم يتم تشغيل الصوت:', error);
        });
    }

    /**
     * إيقاف الصوت الحالي
     */
    stopSound() {
        if (!this.settings.enableAudio || !this.audioPlayer) return;
        
        this.audioPlayer.pause();
        this.audioPlayer.currentTime = 0;
    }
}

// تصدير الكلاس للاستخدام في وحدات أخرى
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CosmicBackground };
} else if (typeof define === 'function' && define.amd) {
    define([], function() { return { CosmicBackground }; });
}