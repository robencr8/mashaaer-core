/**
 * Cultural Themed Loading Animations for Mashaaer Feelings
 * 
 * This script provides functionality for themed loading animations with cultural storytelling elements.
 * It integrates with both cosmic and falling-stars themes of the application.
 */

class CulturalLoader {
  constructor() {
    // Initialize story collections
    this.stories = {
      en: {
        desert: [
          "The camel, known as the 'ship of the desert', has been vital to Arabian culture for thousands of years",
          "Desert travelers navigated by stars, forming a deep connection with the cosmos and astronomy",
          "Nomadic Bedouin tribes developed sophisticated survival skills to thrive in the harshest environments",
          "The Arabian Peninsula contains the Empty Quarter, one of the largest sand deserts in the world"
        ],
        falaj: [
          "The falaj irrigation system has been used in the UAE for over 3,000 years",
          "This ingenious water management system helped transform desert areas into oases of agriculture",
          "Some traditional falaj systems in the UAE are UNESCO World Heritage Sites",
          "The falaj system uses gravity to distribute water from mountain springs to farms"
        ],
        pearl: [
          "Pearl diving was once the UAE's main economic activity before the discovery of oil",
          "Divers would spend months at sea, descending to depths of 40 meters holding only their breath",
          "A skilled diver could collect up to 80 oysters in a single dive",
          "Songs called 'nahma' were sung on pearl diving ships to coordinate the crew's movements"
        ],
        astrolabe: [
          "The astrolabe was perfected by Islamic astronomers during the Golden Age of Science",
          "This ancient instrument was used for navigation, timekeeping, and calculating prayer times",
          "Arab scientists developed the astrolabe as one of history's most important scientific tools",
          "Knowledge of the stars and mathematical precision were hallmarks of Islamic scientific advancement"
        ]
      },
      ar: {
        desert: [
          "الجمل، المعروف باسم 'سفينة الصحراء'، كان حيويًا للثقافة العربية لآلاف السنين",
          "اعتمد المسافرون في الصحراء على النجوم للتنقل، مما أدى إلى ارتباط عميق بالكون وعلم الفلك",
          "طورت قبائل البدو الرحل مهارات بقاء متطورة للازدهار في أقسى البيئات",
          "تحتوي شبه الجزيرة العربية على الربع الخالي، وهي واحدة من أكبر الصحاري الرملية في العالم"
        ],
        falaj: [
          "تم استخدام نظام الري بالفلج في الإمارات لأكثر من 3000 عام",
          "ساعد نظام إدارة المياه الذكي هذا على تحويل المناطق الصحراوية إلى واحات زراعية",
          "بعض أنظمة الفلج التقليدية في الإمارات هي مواقع تراث عالمي لليونسكو",
          "يستخدم نظام الفلج الجاذبية لتوزيع المياه من ينابيع الجبال إلى المزارع"
        ],
        pearl: [
          "كان الغوص بحثًا عن اللؤلؤ النشاط الاقتصادي الرئيسي للإمارات قبل اكتشاف النفط",
          "كان الغواصون يقضون شهورًا في البحر، وينزلون إلى أعماق تصل إلى 40 مترًا وهم يحبسون أنفاسهم فقط",
          "يمكن للغواص الماهر أن يجمع ما يصل إلى 80 محارة في غطسة واحدة",
          "كانت أغاني تسمى 'النهمة' تُغنى على سفن الغوص اللؤلؤية لتنسيق حركات الطاقم"
        ],
        astrolabe: [
          "تم تحسين الإسطرلاب من قبل علماء الفلك المسلمين خلال العصر الذهبي للعلوم",
          "استُخدمت هذه الأداة القديمة للملاحة وقياس الوقت وحساب أوقات الصلاة",
          "طور العلماء العرب الإسطرلاب كواحد من أهم الأدوات العلمية في التاريخ",
          "كانت معرفة النجوم والدقة الرياضية من سمات التقدم العلمي الإسلامي"
        ]
      }
    };
    
    // Track current theme
    this.currentTheme = document.documentElement.getAttribute('data-theme') || 'cosmic';
    
    // Default language
    this.language = document.documentElement.lang || 'en';
    
    // RTL detection
    this.isRTL = document.documentElement.dir === 'rtl';
  }
  
  /**
   * Creates and injects a cultural loader into the specified container
   * 
   * @param {string} containerId - The ID of the container element
   * @param {string} loaderType - The type of loader ('desert', 'falaj', 'pearl', 'astrolabe')
   * @param {Object} options - Optional configuration settings
   * @returns {HTMLElement} - The created loader element
   */
  createLoader(containerId, loaderType = 'desert', options = {}) {
    const container = document.getElementById(containerId);
    if (!container) {
      console.error(`Container with ID '${containerId}' not found`);
      return null;
    }
    
    // Default options
    const defaultOptions = {
      showText: true,
      autoChangeStory: true,
      storyInterval: 4000, // ms
      language: this.language,
      customStories: null
    };
    
    const settings = {...defaultOptions, ...options};
    
    // Create loader container
    const loaderContainer = document.createElement('div');
    loaderContainer.className = 'loader-container';
    loaderContainer.dataset.loaderType = loaderType;
    
    // Create the specific loader based on type
    let loaderElement;
    
    switch (loaderType) {
      case 'desert':
        loaderElement = this._createDesertLoader();
        break;
      case 'falaj':
        loaderElement = this._createFalajLoader();
        break;
      case 'pearl':
        loaderElement = this._createPearlLoader();
        break;
      case 'astrolabe':
        loaderElement = this._createAstrolabeLoader();
        break;
      default:
        loaderElement = this._createDesertLoader();
    }
    
    loaderContainer.appendChild(loaderElement);
    
    // Add storytelling text if enabled
    if (settings.showText) {
      const storyElement = document.createElement('div');
      storyElement.className = 'loader-text';
      
      // Get stories for the selected language and loader type
      let stories = settings.customStories || 
                    this.stories[settings.language]?.[loaderType] ||
                    this.stories['en'][loaderType];
      
      // Set initial story
      let currentStoryIndex = 0;
      storyElement.textContent = stories[currentStoryIndex];
      
      // Set up story rotation if enabled
      if (settings.autoChangeStory && stories.length > 1) {
        const storyInterval = setInterval(() => {
          currentStoryIndex = (currentStoryIndex + 1) % stories.length;
          storyElement.textContent = stories[currentStoryIndex];
        }, settings.storyInterval);
        
        // Store interval for cleanup
        loaderContainer.dataset.storyInterval = storyInterval;
      }
      
      loaderContainer.appendChild(storyElement);
    }
    
    // Add to the container
    container.appendChild(loaderContainer);
    
    return loaderContainer;
  }
  
  /**
   * Removes a loader from the DOM
   * 
   * @param {HTMLElement} loaderElement - The loader element to remove
   */
  removeLoader(loaderElement) {
    if (!loaderElement) return;
    
    // Clear any intervals
    if (loaderElement.dataset.storyInterval) {
      clearInterval(parseInt(loaderElement.dataset.storyInterval));
    }
    
    // Remove from DOM
    loaderElement.remove();
  }
  
  /**
   * Updates the theme for all loaders
   * 
   * @param {string} theme - The theme name ('cosmic' or 'falling-stars')
   */
  updateTheme(theme) {
    this.currentTheme = theme;
    document.documentElement.setAttribute('data-theme', theme);
  }
  
  /**
   * Updates the language for all loader stories
   * 
   * @param {string} language - The language code ('en' or 'ar')
   */
  updateLanguage(language) {
    this.language = language;
    
    // Update existing loader texts
    const loaderTexts = document.querySelectorAll('.loader-text');
    loaderTexts.forEach(textElement => {
      const loaderContainer = textElement.closest('.loader-container');
      if (loaderContainer) {
        const loaderType = loaderContainer.dataset.loaderType;
        const stories = this.stories[language]?.[loaderType] || this.stories['en'][loaderType];
        
        // Update with random story
        const randomIndex = Math.floor(Math.random() * stories.length);
        textElement.textContent = stories[randomIndex];
      }
    });
  }
  
  // Private helper methods to create specific loaders
  _createDesertLoader() {
    const loader = document.createElement('div');
    loader.className = 'loader-desert-caravan cultural-loader';
    
    // Add stars
    for (let i = 0; i < 5; i++) {
      const star = document.createElement('div');
      star.className = 'desert-star';
      loader.appendChild(star);
    }
    
    // Add camel
    const camel = document.createElement('div');
    camel.className = 'desert-camel';
    loader.appendChild(camel);
    
    return loader;
  }
  
  _createFalajLoader() {
    const loader = document.createElement('div');
    loader.className = 'loader-falaj cultural-loader';
    
    // Create channel
    const channel = document.createElement('div');
    channel.className = 'falaj-channel';
    loader.appendChild(channel);
    
    // Create flowing water
    const water = document.createElement('div');
    water.className = 'falaj-water';
    loader.appendChild(water);
    
    // Add plants
    for (let i = 0; i < 3; i++) {
      const plant = document.createElement('div');
      plant.className = 'falaj-plant';
      loader.appendChild(plant);
    }
    
    return loader;
  }
  
  _createPearlLoader() {
    const loader = document.createElement('div');
    loader.className = 'loader-pearl-diving cultural-loader';
    
    // Create sea surface
    const surface = document.createElement('div');
    surface.className = 'sea-surface';
    loader.appendChild(surface);
    
    // Create waves
    const waves = document.createElement('div');
    waves.className = 'sea-waves';
    loader.appendChild(waves);
    
    // Add diver
    const diver = document.createElement('div');
    diver.className = 'diver';
    loader.appendChild(diver);
    
    // Add pearl
    const pearl = document.createElement('div');
    pearl.className = 'pearl';
    loader.appendChild(pearl);
    
    return loader;
  }
  
  _createAstrolabeLoader() {
    const loader = document.createElement('div');
    loader.className = 'loader-astrolabe cultural-loader';
    
    // Create outer ring
    const ring = document.createElement('div');
    ring.className = 'astrolabe-ring';
    loader.appendChild(ring);
    
    // Create arm
    const arm = document.createElement('div');
    arm.className = 'astrolabe-arm';
    loader.appendChild(arm);
    
    // Add cardinal markers
    for (let i = 0; i < 4; i++) {
      const mark = document.createElement('div');
      mark.className = 'astrolabe-mark';
      loader.appendChild(mark);
    }
    
    return loader;
  }
}

// Initialize as global for easy access
window.culturalLoader = new CulturalLoader();

// Listen for theme changes
document.addEventListener('themeChanged', function(e) {
  if (window.culturalLoader) {
    window.culturalLoader.updateTheme(e.detail.theme);
  }
});

// Listen for language changes
document.addEventListener('languageChanged', function(e) {
  if (window.culturalLoader) {
    window.culturalLoader.updateLanguage(e.detail.language);
  }
});