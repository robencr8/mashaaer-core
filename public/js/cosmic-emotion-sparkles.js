/**
 * cosmic-emotion-sparkles.js - تأثيرات مشاعر كونية لتطبيق مشاعر
 * تم تطويره بواسطة فريق مشاعر
 * الإصدار 1.0.0
 */

class ParticleSystem {
    constructor(x, y, color, size, count, container) {
        this.x = x;
        this.y = y;
        this.color = color;
        this.size = size || 3;
        this.count = count || 15;
        this.container = container || document.body;
        this.particles = [];
        this.isActive = false;
        this.containerRect = this.container.getBoundingClientRect();
        
        // إنشاء نظام الجسيمات
        this.create();
    }
    
    create() {
        // إنشاء حاوية للجسيمات
        this.particleContainer = document.createElement('div');
        this.particleContainer.className = 'cosmic-particle-container';
        this.particleContainer.style.position = 'absolute';
        this.particleContainer.style.top = '0';
        this.particleContainer.style.left = '0';
        this.particleContainer.style.width = '100%';
        this.particleContainer.style.height = '100%';
        this.particleContainer.style.pointerEvents = 'none';
        this.particleContainer.style.zIndex = '10000';
        this.particleContainer.style.overflow = 'hidden';
        
        // إذا كانت الحاوية هي الـ body، نجعل الموضع fixed
        if (this.container === document.body) {
            this.particleContainer.style.position = 'fixed';
        }
        
        // إضافة الحاوية إلى الـ DOM
        this.container.appendChild(this.particleContainer);
    }
    
    emit(emotion = 'happy') {
        // إضافة المزيد من الجسيمات بناءً على المشاعر
        const particleCount = emotion === 'angry' ? this.count * 2 : 
                            emotion === 'sad' ? Math.floor(this.count / 2) : 
                            this.count;
        
        // اختيار لون مناسب للمشاعر
        const particleColor = 
            emotion === 'happy' ? '#2dce89' : // أخضر للسعادة
            emotion === 'sad' ? '#11cdef' : // أزرق للحزن
            emotion === 'angry' ? '#f5365c' : // أحمر للغضب
            emotion === 'neutral' ? '#5e72e4' : // أرجواني للحياد
            emotion === 'surprise' ? '#fb6340' : // برتقالي للدهشة
            emotion === 'fear' ? '#825ee4' : // بنفسجي للخوف
            this.color || '#ffffff';
        
        // إنشاء الجسيمات
        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'cosmic-particle';
            
            // تطبيق الأنماط
            particle.style.position = 'absolute';
            particle.style.width = `${this.size}px`;
            particle.style.height = `${this.size}px`;
            particle.style.backgroundColor = particleColor;
            particle.style.borderRadius = '50%';
            particle.style.boxShadow = `0 0 ${this.size * 2}px ${particleColor}`;
            
            // تعيين الموضع الأولي
            const posX = this.x - this.containerRect.left;
            const posY = this.y - this.containerRect.top;
            particle.style.left = `${posX}px`;
            particle.style.top = `${posY}px`;
            
            // إضافة الجسيم إلى الحاوية
            this.particleContainer.appendChild(particle);
            
            // تعيين خصائص الحركة العشوائية
            const angle = Math.random() * Math.PI * 2;
            const speed = Math.random() * 5 + 3;
            const distance = Math.random() * 100 + 50;
            const lifeTime = Math.random() * 1000 + 500;
            const delay = Math.random() * 200;
            
            // إنشاء نمط الرسوم المتحركة الفريد لكل جسيم
            const keyframes = [
                { 
                    transform: `translate(0, 0) scale(1)`,
                    opacity: 1
                },
                { 
                    transform: `translate(${Math.cos(angle) * distance}px, ${Math.sin(angle) * distance}px) scale(0)`,
                    opacity: 0
                }
            ];
            
            // الخصائص المحددة للرسوم المتحركة
            const animOptions = {
                duration: lifeTime,
                delay: delay,
                easing: 'cubic-bezier(0.25, 0.1, 0.25, 1)',
                fill: 'forwards'
            };
            
            // تعديل نمط الحركة بناءً على المشاعر
            if (emotion === 'happy') {
                // حركة أكثر انتعاشًا وسريعة
                animOptions.easing = 'cubic-bezier(0.1, 0.9, 0.2, 1)';
            } else if (emotion === 'sad') {
                // حركة أبطأ وأكثر انحناء
                animOptions.easing = 'cubic-bezier(0.7, 0.1, 0.9, 0.2)';
                animOptions.duration = lifeTime * 1.5;
            } else if (emotion === 'angry') {
                // حركة عنيفة ومتقطعة
                keyframes.splice(1, 0, {
                    transform: `translate(${Math.cos(angle) * distance * 0.5}px, ${Math.sin(angle) * distance * 0.5}px) scale(0.7)`,
                    opacity: 0.7
                });
                animOptions.easing = 'cubic-bezier(0.1, 0.2, 0.7, 0.1)';
            }
            
            // بدء الرسوم المتحركة
            const animation = particle.animate(keyframes, animOptions);
            
            // إزالة الجسيم عند انتهاء الرسوم المتحركة
            animation.onfinish = () => {
                particle.remove();
            };
            
            // حفظ الجسيم في المصفوفة
            this.particles.push({
                element: particle,
                animation: animation
            });
        }
    }
    
    update(x, y) {
        this.x = x;
        this.y = y;
    }
    
    stop() {
        // إيقاف جميع الرسوم المتحركة
        this.particles.forEach(particle => {
            particle.animation.cancel();
            particle.element.remove();
        });
        this.particles = [];
    }
    
    cleanup() {
        this.stop();
        if (this.particleContainer) {
            this.particleContainer.remove();
        }
    }
}

class EmotionSparkles {
    constructor(options = {}) {
        this.options = {
            container: options.container || document.body,
            enabled: options.enabled !== undefined ? options.enabled : true,
            size: options.size || 5,
            count: options.count || 20,
            clickEnabled: options.clickEnabled !== undefined ? options.clickEnabled : true,
            hoverEnabled: options.hoverEnabled !== undefined ? options.hoverEnabled : true,
            emotionChangeEnabled: options.emotionChangeEnabled !== undefined ? options.emotionChangeEnabled : true
        };
        
        this.currentEmotion = 'neutral';
        this.lastEmitTime = 0;
        this.emotionChangeCooldown = 500; // وقت الانتظار بين تغييرات المشاعر بالمللي ثانية
        
        this.systems = {};
        
        if (this.options.enabled) {
            this.init();
        }
    }
    
    init() {
        // تتبع النقرات وإضافة تأثيرات
        if (this.options.clickEnabled) {
            document.addEventListener('click', (e) => {
                this.emitFromEvent(e, this.currentEmotion);
            });
        }
        
        // تتبع عناصر المشاعر المحددة
        if (this.options.emotionChangeEnabled) {
            document.addEventListener('mouseover', (e) => {
                // البحث عن اقرب عنصر يحتوي على سمة data-emotion
                let target = e.target;
                while (target && target !== document.body) {
                    if (target.dataset.emotion) {
                        if (this.options.hoverEnabled) {
                            const rect = target.getBoundingClientRect();
                            const x = rect.left + rect.width / 2;
                            const y = rect.top + rect.height / 2;
                            
                            this.setEmotion(target.dataset.emotion);
                            this.emit(x, y, target.dataset.emotion);
                        }
                        break;
                    }
                    target = target.parentElement;
                }
            });
        }
    }
    
    emitFromEvent(event, emotion = null) {
        const x = event.clientX;
        const y = event.clientY;
        this.emit(x, y, emotion || this.currentEmotion);
    }
    
    emit(x, y, emotion = null) {
        const now = Date.now();
        
        // الانتظار قبل إصدار المزيد من الجسيمات
        if (now - this.lastEmitTime < this.emotionChangeCooldown) {
            return;
        }
        
        const key = `${x}-${y}`;
        if (!this.systems[key]) {
            this.systems[key] = new ParticleSystem(
                x, y, 
                null, 
                this.options.size, 
                this.options.count, 
                this.options.container
            );
        }
        
        this.systems[key].update(x, y);
        this.systems[key].emit(emotion || this.currentEmotion);
        
        this.lastEmitTime = now;
        
        // تنظيف النظام بعد فترة
        setTimeout(() => {
            if (this.systems[key]) {
                this.systems[key].cleanup();
                delete this.systems[key];
            }
        }, 2000);
    }
    
    setEmotion(emotion) {
        this.currentEmotion = emotion;
    }
}

// تسجيل الكلاس للاستخدام العالمي
window.EmotionSparkles = EmotionSparkles;
window.ParticleSystem = ParticleSystem;