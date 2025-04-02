/**
 * Chart Renderer for Robin AI
 * Handles visualization of emotion data using Chart.js
 */
class ChartRenderer {
    constructor(options = {}) {
        this.timelineChartId = options.timelineChartId || 'emotion-timeline-chart';
        this.distributionChartId = options.distributionChartId || 'emotion-distribution-chart';
        this.entriesTrendChartId = options.entriesTrendChartId || 'entries-trend-chart';
        
        this.timelineChart = null;
        this.distributionChart = null;
        this.entriesTrendChart = null;
        
        // Default colors for emotions
        this.emotionColors = {
            'neutral': 'rgba(54, 162, 235, 0.7)',
            'happy': 'rgba(75, 192, 192, 0.7)',
            'sad': 'rgba(201, 203, 207, 0.7)',
            'angry': 'rgba(255, 99, 132, 0.7)',
            'fearful': 'rgba(255, 205, 86, 0.7)',
            'disgusted': 'rgba(153, 102, 255, 0.7)',
            'surprised': 'rgba(255, 159, 64, 0.7)',
            'confused': 'rgba(231, 233, 237, 0.7)',
            'interested': 'rgba(46, 204, 113, 0.7)'
        };
        
        // Border colors (darker version of fill colors)
        this.emotionBorders = {
            'neutral': 'rgba(54, 162, 235, 1)',
            'happy': 'rgba(75, 192, 192, 1)',
            'sad': 'rgba(201, 203, 207, 1)',
            'angry': 'rgba(255, 99, 132, 1)',
            'fearful': 'rgba(255, 205, 86, 1)',
            'disgusted': 'rgba(153, 102, 255, 1)',
            'surprised': 'rgba(255, 159, 64, 1)',
            'confused': 'rgba(231, 233, 237, 1)',
            'interested': 'rgba(46, 204, 113, 1)'
        };
        
        // Emotion icons (Font Awesome classes)
        this.emotionIcons = {
            'neutral': 'fa-meh',
            'happy': 'fa-smile',
            'sad': 'fa-frown',
            'angry': 'fa-angry',
            'fearful': 'fa-grimace',
            'disgusted': 'fa-dizzy',
            'surprised': 'fa-surprise',
            'confused': 'fa-question-circle',
            'interested': 'fa-grin-stars'
        };
    }
    
    /**
     * Render the emotion timeline chart
     * @param {Object} data - The emotion data object from the API
     */
    renderTimelineChart(data) {
        const ctx = document.getElementById(this.timelineChartId);
        
        if (!ctx) {
            console.error(`Canvas element with ID ${this.timelineChartId} not found`);
            return;
        }
        
        // If chart already exists, destroy it
        if (this.timelineChart) {
            this.timelineChart.destroy();
        }
        
        // Format datasets with colors
        const datasets = [];
        
        if (data && data.datasets) {
            data.datasets.forEach(dataset => {
                const emotion = dataset.label.toLowerCase();
                datasets.push({
                    label: dataset.label,
                    data: dataset.data,
                    backgroundColor: this.emotionColors[emotion] || 'rgba(100, 100, 100, 0.7)',
                    borderColor: this.emotionBorders[emotion] || 'rgba(100, 100, 100, 1)',
                    borderWidth: 1
                });
            });
        }
        
        // Create stacked bar chart
        this.timelineChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels || [],
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Emotion Timeline',
                        font: {
                            size: 16
                        }
                    },
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    x: {
                        stacked: true,
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    },
                    y: {
                        stacked: true,
                        title: {
                            display: true,
                            text: 'Count'
                        },
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    /**
     * Render the emotion distribution pie chart
     * @param {Object} data - The emotion data object from the API
     */
    renderDistributionChart(data) {
        const ctx = document.getElementById(this.distributionChartId);
        
        if (!ctx) {
            console.error(`Canvas element with ID ${this.distributionChartId} not found`);
            return;
        }
        
        // If chart already exists, destroy it
        if (this.distributionChart) {
            this.distributionChart.destroy();
        }
        
        // Calculate totals for each emotion
        const emotionTotals = {};
        const backgroundColors = [];
        const borderColors = [];
        
        if (data && data.datasets) {
            data.datasets.forEach(dataset => {
                const emotion = dataset.label.toLowerCase();
                const total = dataset.data.reduce((sum, count) => sum + count, 0);
                emotionTotals[dataset.label] = total;
                
                backgroundColors.push(this.emotionColors[emotion] || 'rgba(100, 100, 100, 0.7)');
                borderColors.push(this.emotionBorders[emotion] || 'rgba(100, 100, 100, 1)');
            });
        }
        
        // Create pie chart
        this.distributionChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: Object.keys(emotionTotals),
                datasets: [{
                    data: Object.values(emotionTotals),
                    backgroundColor: backgroundColors,
                    borderColor: borderColors,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    /**
     * Render the entries trend line chart
     * @param {Object} data - The emotion data object from the API
     */
    renderEntriesTrendChart(data) {
        const ctx = document.getElementById(this.entriesTrendChartId);
        
        if (!ctx) {
            console.error(`Canvas element with ID ${this.entriesTrendChartId} not found`);
            return;
        }
        
        // If chart already exists, destroy it
        if (this.entriesTrendChart) {
            this.entriesTrendChart.destroy();
        }
        
        // Calculate total entries per day
        const dailyTotals = [];
        
        if (data && data.datasets && data.labels) {
            // For each day, sum all emotion counts
            for (let i = 0; i < data.labels.length; i++) {
                let dayTotal = 0;
                data.datasets.forEach(dataset => {
                    dayTotal += dataset.data[i] || 0;
                });
                dailyTotals.push(dayTotal);
            }
        }
        
        // Create line chart
        this.entriesTrendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels || [],
                datasets: [{
                    label: 'Total Entries',
                    data: dailyTotals,
                    fill: false,
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    tension: 0.1,
                    pointBackgroundColor: 'rgba(75, 192, 192, 1)',
                    pointBorderColor: '#fff',
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Count'
                        }
                    }
                }
            }
        });
    }
    
    /**
     * Update chart visibility based on emotion filters
     * @param {Object} filters - Object with emotion names as keys and boolean values
     */
    updateEmotionFilters(filters) {
        if (!this.timelineChart) return;
        
        this.timelineChart.data.datasets.forEach((dataset, index) => {
            const emotion = dataset.label.toLowerCase();
            const isVisible = filters[emotion];
            
            this.timelineChart.setDatasetVisibility(index, isVisible);
        });
        
        this.timelineChart.update();
        
        // Also update distribution chart if it exists
        if (this.distributionChart) {
            const visibleEmotions = {};
            
            this.timelineChart.data.datasets.forEach((dataset, index) => {
                const emotion = dataset.label;
                visibleEmotions[emotion] = this.timelineChart.isDatasetVisible(index);
            });
            
            // Filter distribution chart data
            const filteredLabels = [];
            const filteredData = [];
            const filteredColors = [];
            const filteredBorders = [];
            
            this.distributionChart.data.labels.forEach((label, i) => {
                if (visibleEmotions[label]) {
                    filteredLabels.push(label);
                    filteredData.push(this.distributionChart.data.datasets[0].data[i]);
                    filteredColors.push(this.distributionChart.data.datasets[0].backgroundColor[i]);
                    filteredBorders.push(this.distributionChart.data.datasets[0].borderColor[i]);
                }
            });
            
            this.distributionChart.data.labels = filteredLabels;
            this.distributionChart.data.datasets[0].data = filteredData;
            this.distributionChart.data.datasets[0].backgroundColor = filteredColors;
            this.distributionChart.data.datasets[0].borderColor = filteredBorders;
            
            this.distributionChart.update();
        }
    }
    
    /**
     * Get emotion icon class based on emotion name
     * @param {string} emotion - The emotion name
     * @returns {string} - Font Awesome icon class
     */
    getEmotionIcon(emotion) {
        const lowercaseEmotion = emotion.toLowerCase();
        return this.emotionIcons[lowercaseEmotion] || 'fa-meh';
    }
    
    /**
     * Get color for an emotion
     * @param {string} emotion - The emotion name
     * @returns {string} - CSS color value
     */
    getEmotionColor(emotion) {
        const lowercaseEmotion = emotion.toLowerCase();
        return this.emotionColors[lowercaseEmotion] || 'rgba(100, 100, 100, 0.7)';
    }
}
