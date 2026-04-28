// WordMaster 应用程序主逻辑
class WordMasterApp {
    constructor() {
        this.currentUser = {
            name: '学习者',
            streakDays: 0,
            totalWords: 0,
            masteredWords: 0,
            accuracyRate: 0,
            studyTime: 0,
            totalQuizzes: 0
        };
        
        this.learningProgress = {
            newWordsToday: 0,
            reviewWordsToday: 0,
            dailyGoal: 10,
            reviewGoal: 20,
            wordStatus: {}, // 单词状态: new, learning, reviewing, mastered, difficult
            wordHistory: [],
            quizHistory: [],
            studyHistory: []
        };
        
        this.currentStudy = {
            book: null,
            currentIndex: 0,
            words: []
        };
        
        this.currentQuiz = {
            mode: 'cn-to-en',
            count: 20,
            questions: [],
            currentIndex: 0,
            score: 0,
            startTime: null,
            answers: []
        };
        
        this.settings = {
            autoPronunciation: true,
            dailyGoal: 10,
            reviewGoal: 20
        };
        
        this.init();
    }
    
    init() {
        this.loadData();
        this.bindEvents();
        this.updateStats();
        this.renderHome();
        this.checkDailyStreak();
    }
    
    // 数据持久化
    loadData() {
        const saved = localStorage.getItem('wordmaster_data');
        if (saved) {
            const data = JSON.parse(saved);
            this.currentUser = { ...this.currentUser, ...data.currentUser };
            this.learningProgress = { ...this.learningProgress, ...data.learningProgress };
            this.settings = { ...this.settings, ...data.settings };
        }
    }
    
    saveData() {
        const data = {
            currentUser: this.currentUser,
            learningProgress: this.learningProgress,
            settings: this.settings
        };
        localStorage.setItem('wordmaster_data', JSON.stringify(data));
    }
    
    // 事件绑定
    bindEvents() {
        // 导航切换
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const page = e.currentTarget.dataset.page;
                this.navigateTo(page);
            });
        });
        
        // 词库选择
        document.querySelectorAll('.wordbook-card').forEach(card => {
            card.addEventListener('click', () => {
                const book = card.dataset.book;
                this.startStudy(book);
            });
        });
        
        // 学习按钮
        document.getElementById('btn-forget')?.addEventListener('click', () => this.handleStudy('forget'));
        document.getElementById('btn-vague')?.addEventListener('click', () => this.handleStudy('vague'));
        document.getElementById('btn-know')?.addEventListener('click', () => this.handleStudy('know'));
        
        // 发音按钮
        document.getElementById('play-audio')?.addEventListener('click', () => this.playCurrentWord());
        
        // 测试设置
        document.querySelectorAll('.option-btn[data-mode]').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.option-btn[data-mode]').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.currentQuiz.mode = btn.dataset.mode;
            });
        });
        
        document.querySelectorAll('.option-btn[data-count]').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.option-btn[data-count]').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.currentQuiz.count = parseInt(btn.dataset.count);
            });
        });
        
        // 开始测试
        document.getElementById('start-quiz')?.addEventListener('click', () => this.startQuiz());
        
        // 设置页面
        document.getElementById('daily-goal')?.addEventListener('change', (e) => {
            this.settings.dailyGoal = parseInt(e.target.value);
            this.learningProgress.dailyGoal = this.settings.dailyGoal;
            this.saveData();
            this.updateStats();
        });
        
        document.getElementById('review-goal')?.addEventListener('change', (e) => {
            this.settings.reviewGoal = parseInt(e.target.value);
            this.learningProgress.reviewGoal = this.settings.reviewGoal;
            this.saveData();
            this.updateStats();
        });
        
        document.getElementById('auto-pronunciation')?.addEventListener('change', (e) => {
            this.settings.autoPronunciation = e.target.checked;
            this.saveData();
        });
        
        // 数据管理
        document.getElementById('export-data')?.addEventListener('click', () => this.exportData());
        document.getElementById('import-data')?.addEventListener('change', (e) => this.importData(e));
        document.getElementById('clear-data')?.addEventListener('click', () => this.clearData());
        
        // 单词状态筛选
        document.querySelectorAll('.status-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.status-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                this.renderWordList(tab.dataset.status);
            });
        });
    }
    
    // 页面导航
    navigateTo(page) {
        // 更新导航状态
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.page === page) {
                item.classList.add('active');
            }
        });
        
        // 切换页面
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
        document.getElementById(page).classList.add('active');
        
        // 页面特定初始化
        if (page === 'home') {
            this.updateStats();
            this.renderHome();
        } else if (page === 'review') {
            this.renderReview();
        } else if (page === 'progress') {
            this.renderProgress();
        } else if (page === 'settings') {
            this.loadSettings();
        }
    }
    
    // 更新统计数据
    updateStats() {
        document.getElementById('total-words').textContent = this.currentUser.totalWords;
        document.getElementById('streak-days').textContent = this.currentUser.streakDays;
        document.getElementById('accuracy-rate').textContent = this.currentUser.accuracyRate + '%';
        document.getElementById('mastered-words').textContent = this.currentUser.masteredWords;
        
        // 更新进度条
        const newProgress = Math.min((this.learningProgress.newWordsToday / this.learningProgress.dailyGoal) * 100, 100);
        const reviewProgress = Math.min((this.learningProgress.reviewWordsToday / this.learningProgress.reviewGoal) * 100, 100);
        
        document.getElementById('new-words-progress').style.width = newProgress + '%';
        document.getElementById('review-words-progress').style.width = reviewProgress + '%';
        document.getElementById('new-words-count').textContent = this.learningProgress.newWordsToday;
        document.getElementById('review-words-count').textContent = this.learningProgress.reviewWordsToday;
    }
    
    // 渲染首页
    renderHome() {
        // 更新词库进度
        document.querySelectorAll('.wordbook-card').forEach(card => {
            const book = card.dataset.book;
            const learned = this.getLearnedCount(book);
            const total = wordDatabase[book]?.length || 0;
            card.querySelector('.wordbook-progress').textContent = `${learned}/${total}`;
        });
    }
    
    // 获取已学单词数
    getLearnedCount(book) {
        return Object.entries(this.learningProgress.wordStatus)
            .filter(([word, status]) => {
                const wordData = this.findWord(word);
                return wordData && status.book === book && status.status !== 'new';
            }).length;
    }
    
    // 查找单词
    findWord(word) {
        for (const book in wordDatabase) {
            const found = wordDatabase[book].find(w => w.word === word);
            if (found) return { ...found, book };
        }
        return null;
    }
    
    // 开始学习
    startStudy(book) {
        this.currentStudy.book = book;
        this.currentStudy.words = [...wordDatabase[book]];
        this.currentStudy.currentIndex = 0;
        
        // 过滤已掌握的单词
        this.currentStudy.words = this.currentStudy.words.filter(w => {
            const status = this.learningProgress.wordStatus[w.word];
            return !status || status.status !== 'mastered';
        });
        
        if (this.currentStudy.words.length === 0) {
            this.showNotification('该词库已全部掌握！', 'success');
            return;
        }
        
        // 显示学习区域
        document.querySelector('.wordbook-selector').style.display = 'none';
        document.getElementById('study-area').style.display = 'block';
        
        this.showCurrentWord();
    }
    
    // 显示当前单词
    showCurrentWord() {
        const word = this.currentStudy.words[this.currentStudy.currentIndex];
        if (!word) {
            this.finishStudy();
            return;
        }
        
        document.getElementById('word-tag').textContent = this.currentStudy.book.toUpperCase();
        document.getElementById('word-text').textContent = word.word;
        document.getElementById('word-phonetic').textContent = word.phonetic;
        document.getElementById('word-meaning').innerHTML = `<p class="meaning-text">${word.meaning}</p>`;
        document.getElementById('word-example').innerHTML = `
            <p class="example-en">${word.example.en}</p>
            <p class="example-cn">${word.example.cn}</p>
        `;
        
        if (this.settings.autoPronunciation) {
            this.playWord(word.word);
        }
    }
    
    // 播放单词发音
    playWord(word) {
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(word);
            utterance.lang = 'en-US';
            utterance.rate = 0.8;
            speechSynthesis.speak(utterance);
        }
    }
    
    playCurrentWord() {
        const word = this.currentStudy.words[this.currentStudy.currentIndex];
        if (word) {
            this.playWord(word.word);
        }
    }
    
    // 处理学习反馈
    handleStudy(level) {
        const word = this.currentStudy.words[this.currentStudy.currentIndex];
        const statusMap = {
            'forget': 'difficult',
            'vague': 'learning',
            'know': 'mastered'
        };
        
        // 更新单词状态
        this.learningProgress.wordStatus[word.word] = {
            status: statusMap[level],
            book: this.currentStudy.book,
            lastReview: new Date().toISOString(),
            reviewCount: (this.learningProgress.wordStatus[word.word]?.reviewCount || 0) + 1
        };
        
        // 更新统计
        if (!this.learningProgress.wordHistory.includes(word.word)) {
            this.learningProgress.wordHistory.push(word.word);
            this.currentUser.totalWords++;
            this.learningProgress.newWordsToday++;
        }
        
        if (level === 'know') {
            this.currentUser.masteredWords++;
        }
        
        // 记录学习历史
        this.learningProgress.studyHistory.push({
            word: word.word,
            level: level,
            time: new Date().toISOString()
        });
        
        this.saveData();
        this.updateStats();
        
        // 下一个单词
        this.currentStudy.currentIndex++;
        if (this.currentStudy.currentIndex >= this.currentStudy.words.length) {
            this.finishStudy();
        } else {
            this.showCurrentWord();
        }
    }
    
    // 完成学习
    finishStudy() {
        document.querySelector('.wordbook-selector').style.display = 'block';
        document.getElementById('study-area').style.display = 'none';
        this.showNotification('学习完成！', 'success');
        this.updateStats();
    }
    
    // 显示测试设置
    showQuizSetup() {
        document.getElementById('quiz-setup').style.display = 'block';
        document.getElementById('quiz-area').style.display = 'none';
        document.getElementById('quiz-result').style.display = 'none';
    }
    
    // 开始测试
    startQuiz() {
        // 获取已学单词
        const learnedWords = Object.keys(this.learningProgress.wordStatus)
            .filter(w => this.learningProgress.wordStatus[w].status !== 'new')
            .map(w => this.findWord(w))
            .filter(w => w !== null);
        
        if (learnedWords.length < 4) {
            this.showNotification('请先学习一些单词再测试！', 'error');
            return;
        }
        
        // 生成题目
        const count = Math.min(this.currentQuiz.count, learnedWords.length);
        this.currentQuiz.questions = this.generateQuestions(learnedWords, count);
        this.currentQuiz.currentIndex = 0;
        this.currentQuiz.score = 0;
        this.currentQuiz.startTime = Date.now();
        this.currentQuiz.answers = [];
        
        document.getElementById('quiz-setup').style.display = 'none';
        document.getElementById('quiz-area').style.display = 'block';
        document.getElementById('quiz-result').style.display = 'none';
        document.getElementById('total-questions').textContent = count;
        
        this.showQuestion();
    }
    
    // 生成题目
    generateQuestions(words, count) {
        const shuffled = [...words].sort(() => Math.random() - 0.5);
        const selected = shuffled.slice(0, count);
        
        return selected.map(word => {
            const options = this.generateOptions(word, words);
            return {
                word: word,
                options: options,
                correct: options.indexOf(word)
            };
        });
    }
    
    // 生成选项
    generateOptions(correctWord, allWords) {
        const options = [correctWord];
        const others = allWords.filter(w => w.word !== correctWord.word)
            .sort(() => Math.random() - 0.5)
            .slice(0, 3);
        options.push(...others);
        return options.sort(() => Math.random() - 0.5);
    }
    
    // 显示题目
    showQuestion() {
        const question = this.currentQuiz.questions[this.currentQuiz.currentIndex];
        const progress = ((this.currentQuiz.currentIndex + 1) / this.currentQuiz.questions.length) * 100;
        
        document.getElementById('quiz-progress-fill').style.width = progress + '%';
        document.getElementById('current-question').textContent = this.currentQuiz.currentIndex + 1;
        
        // 根据模式显示题目
        let questionText;
        if (this.currentQuiz.mode === 'cn-to-en') {
            questionText = `选择 "${question.word.meaning.split(' ')[1]}" 对应的英文单词`;
        } else if (this.currentQuiz.mode === 'en-to-cn') {
            questionText = `"${question.word.word}" 的中文意思是？`;
        } else {
            questionText = Math.random() > 0.5 
                ? `选择 "${question.word.meaning.split(' ')[1]}" 对应的英文单词`
                : `"${question.word.word}" 的中文意思是？`;
        }
        
        document.getElementById('quiz-question').textContent = questionText;
        
        // 生成选项
        const optionsContainer = document.getElementById('quiz-options');
        optionsContainer.innerHTML = '';
        
        question.options.forEach((option, index) => {
            const btn = document.createElement('button');
            btn.className = 'quiz-option';
            
            if (this.currentQuiz.mode === 'en-to-cn' || 
                (this.currentQuiz.mode === 'mixed' && questionText.includes('中文'))) {
                btn.textContent = option.meaning;
            } else {
                btn.textContent = option.word;
            }
            
            btn.addEventListener('click', () => this.answerQuestion(index));
            optionsContainer.appendChild(btn);
        });
    }
    
    // 回答问题
    answerQuestion(answerIndex) {
        const question = this.currentQuiz.questions[this.currentQuiz.currentIndex];
        const isCorrect = answerIndex === question.correct;
        
        if (isCorrect) {
            this.currentQuiz.score++;
        }
        
        this.currentQuiz.answers.push({
            word: question.word.word,
            correct: isCorrect
        });
        
        // 显示正确/错误
        const options = document.querySelectorAll('.quiz-option');
        options[question.correct].classList.add('correct');
        if (!isCorrect) {
            options[answerIndex].classList.add('wrong');
        }
        
        // 延迟下一题
        setTimeout(() => {
            this.currentQuiz.currentIndex++;
            if (this.currentQuiz.currentIndex >= this.currentQuiz.questions.length) {
                this.finishQuiz();
            } else {
                this.showQuestion();
            }
        }, 1000);
    }
    
    // 完成测试
    finishQuiz() {
        const total = this.currentQuiz.questions.length;
        const score = this.currentQuiz.score;
        const accuracy = Math.round((score / total) * 100);
        const timeSpent = Math.floor((Date.now() - this.currentQuiz.startTime) / 1000);
        const minutes = Math.floor(timeSpent / 60);
        const seconds = timeSpent % 60;
        
        // 更新用户统计
        this.currentUser.totalQuizzes++;
        this.currentUser.accuracyRate = Math.round(
            ((this.currentUser.accuracyRate * (this.currentUser.totalQuizzes - 1)) + accuracy) / this.currentUser.totalQuizzes
        );
        
        // 记录测试历史
        this.learningProgress.quizHistory.push({
            score: score,
            total: total,
            accuracy: accuracy,
            time: new Date().toISOString()
        });
        
        this.saveData();
        this.updateStats();
        
        // 显示结果
        document.getElementById('quiz-area').style.display = 'none';
        document.getElementById('quiz-result').style.display = 'block';
        
        document.getElementById('score-value').textContent = score;
        document.getElementById('score-total').textContent = `/ ${total}`;
        document.getElementById('result-accuracy').textContent = accuracy + '%';
        document.getElementById('result-time').textContent = 
            `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        // 评价信息
        let message;
        if (accuracy >= 90) message = '太棒了！完美掌握！🎉';
        else if (accuracy >= 80) message = '非常好！继续加油！👏';
        else if (accuracy >= 60) message = '不错！还有进步空间！💪';
        else message = '继续练习，你会进步的！📚';
        document.getElementById('result-message').textContent = message;
    }
    
    // 重新测试
    restartQuiz() {
        this.startQuiz();
    }
    
    // 渲染复习页面
    renderReview() {
        const dueWords = this.getDueWords();
        document.getElementById('due-today').textContent = dueWords.length;
        
        const listContainer = document.getElementById('review-list');
        
        if (dueWords.length === 0) {
            listContainer.innerHTML = `
                <div class="empty-state">
                    <span class="empty-icon">🎊</span>
                    <p>太棒了！今日没有待复习的单词</p>
                    <button class="action-btn primary" onclick="app.navigateTo('study')">去学习新单词</button>
                </div>
            `;
        } else {
            listContainer.innerHTML = dueWords.map(word => `
                <div class="word-item">
                    <div class="word-info">
                        <h4>${word.word}</h4>
                        <p>${word.meaning}</p>
                    </div>
                    <button class="action-btn secondary" onclick="app.reviewWord('${word.word}')">复习</button>
                </div>
            `).join('');
        }
    }
    
    // 获取待复习单词
    getDueWords() {
        const now = new Date();
        return Object.entries(this.learningProgress.wordStatus)
            .filter(([word, status]) => {
                if (status.status === 'mastered' || status.status === 'new') return false;
                const lastReview = new Date(status.lastReview);
                const daysSinceReview = (now - lastReview) / (1000 * 60 * 60 * 24);
                
                // 根据状态决定复习间隔
                const intervals = { learning: 1, reviewing: 3, difficult: 1 };
                return daysSinceReview >= (intervals[status.status] || 1);
            })
            .map(([word]) => this.findWord(word))
            .filter(w => w !== null)
            .slice(0, this.learningProgress.reviewGoal);
    }
    
    // 复习单词
    reviewWord(wordText) {
        const word = this.findWord(wordText);
        if (!word) return;
        
        // 创建复习弹窗
        const modal = document.createElement('div');
        modal.className = 'review-modal';
        modal.innerHTML = `
            <div class="review-modal-content">
                <div class="word-card">
                    <h2>${word.word}</h2>
                    <p class="word-phonetic">${word.phonetic}</p>
                    <div class="word-meaning">
                        <p>${word.meaning}</p>
                    </div>
                    <div class="word-example">
                        <p class="example-en">${word.example.en}</p>
                        <p class="example-cn">${word.example.cn}</p>
                    </div>
                </div>
                <div class="review-actions">
                    <button class="study-btn forget" onclick="app.finishReview('${word.word}', 'difficult')">😕 仍不熟悉</button>
                    <button class="study-btn know" onclick="app.finishReview('${word.word}', 'mastered')">😊 已掌握</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        this.playWord(word.word);
    }
    
    // 完成复习
    finishReview(word, result) {
        this.learningProgress.wordStatus[word].status = result;
        this.learningProgress.wordStatus[word].lastReview = new Date().toISOString();
        this.learningProgress.reviewWordsToday++;
        
        if (result === 'mastered') {
            this.currentUser.masteredWords++;
        }
        
        this.saveData();
        this.updateStats();
        
        // 关闭弹窗
        document.querySelector('.review-modal')?.remove();
        this.renderReview();
    }
    
    // 渲染进度页面
    renderProgress() {
        // 更新概览数据
        document.getElementById('total-study-time').textContent = 
            Math.floor(this.currentUser.studyTime / 60) + '小时';
        document.getElementById('total-quizzes').textContent = 
            this.currentUser.totalQuizzes + '次';
        document.getElementById('avg-accuracy').textContent = 
            this.currentUser.accuracyRate + '%';
        
        // 渲染图表
        this.renderStudyChart();
        
        // 渲染单词列表
        this.renderWordList('all');
    }
    
    // 渲染学习图表
    renderStudyChart() {
        const chart = document.getElementById('study-chart');
        const last7Days = this.getLast7DaysData();
        
        const maxValue = Math.max(...last7Days.map(d => d.count), 1);
        
        chart.innerHTML = last7Days.map(day => `
            <div class="chart-bar" style="height: ${(day.count / maxValue) * 100}%">
                <span class="chart-label">${day.label}</span>
            </div>
        `).join('');
    }
    
    // 获取最近7天数据
    getLast7DaysData() {
        const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
        const result = [];
        
        for (let i = 6; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            const dateStr = date.toDateString();
            
            const count = this.learningProgress.studyHistory.filter(h => 
                new Date(h.time).toDateString() === dateStr
            ).length;
            
            result.push({
                label: i === 0 ? '今天' : days[date.getDay()],
                count: count
            });
        }
        
        return result;
    }
    
    // 渲染单词列表
    renderWordList(filter) {
        const list = document.getElementById('word-list');
        let words = Object.entries(this.learningProgress.wordStatus)
            .filter(([word, status]) => {
                if (filter === 'all') return status.status !== 'new';
                return status.status === filter;
            })
            .map(([word, status]) => ({
                ...this.findWord(word),
                status: status.status
            }))
            .filter(w => w.word);
        
        if (words.length === 0) {
            list.innerHTML = '<div class="empty-state"><p>暂无单词</p></div>';
            return;
        }
        
        list.innerHTML = words.map(w => `
            <div class="word-item">
                <div class="word-info">
                    <h4>${w.word}</h4>
                    <p>${w.meaning}</p>
                </div>
                <span class="word-status ${w.status}">${this.getStatusLabel(w.status)}</span>
            </div>
        `).join('');
    }
    
    getStatusLabel(status) {
        const labels = {
            new: '新词',
            learning: '学习中',
            reviewing: '复习中',
            mastered: '已掌握',
            difficult: '困难词'
        };
        return labels[status] || status;
    }
    
    // 加载设置
    loadSettings() {
        document.getElementById('daily-goal').value = this.settings.dailyGoal;
        document.getElementById('review-goal').value = this.settings.reviewGoal;
        document.getElementById('auto-pronunciation').checked = this.settings.autoPronunciation;
    }
    
    // 检查连续学习天数
    checkDailyStreak() {
        const today = new Date().toDateString();
        const lastStudy = localStorage.getItem('wordmaster_last_study');
        
        if (lastStudy) {
            const lastDate = new Date(lastStudy);
            const yesterday = new Date();
            yesterday.setDate(yesterday.getDate() - 1);
            
            if (lastDate.toDateString() === yesterday.toDateString()) {
                // 连续学习
            } else if (lastDate.toDateString() !== today) {
                // 中断了
                this.currentUser.streakDays = 0;
                this.learningProgress.newWordsToday = 0;
                this.learningProgress.reviewWordsToday = 0;
                this.saveData();
            }
        }
    }
    
    // 导出数据
    exportData() {
        const data = {
            currentUser: this.currentUser,
            learningProgress: this.learningProgress,
            settings: this.settings,
            exportDate: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `wordmaster_backup_${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
        
        this.showNotification('数据导出成功！', 'success');
    }
    
    // 导入数据
    importData(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const data = JSON.parse(e.target.result);
                if (data.currentUser && data.learningProgress) {
                    this.currentUser = { ...this.currentUser, ...data.currentUser };
                    this.learningProgress = { ...this.learningProgress, ...data.learningProgress };
                    if (data.settings) {
                        this.settings = { ...this.settings, ...data.settings };
                    }
                    this.saveData();
                    this.updateStats();
                    this.showNotification('数据导入成功！', 'success');
                } else {
                    throw new Error('Invalid data format');
                }
            } catch (err) {
                this.showNotification('数据导入失败，请检查文件格式', 'error');
            }
        };
        reader.readAsText(file);
    }
    
    // 清除数据
    clearData() {
        if (confirm('确定要清除所有学习数据吗？此操作不可恢复！')) {
            localStorage.removeItem('wordmaster_data');
            location.reload();
        }
    }
    
    // 显示通知
    showNotification(message, type = 'success') {
        const notification = document.getElementById('notification');
        notification.querySelector('.notification-message').textContent = message;
        notification.querySelector('.notification-icon').textContent = type === 'success' ? '✓' : '✗';
        notification.classList.add('show');
        
        setTimeout(() => {
            notification.classList.remove('show');
        }, 3000);
    }
}

// 初始化应用
const app = new WordMasterApp();

// 添加复习弹窗样式
const style = document.createElement('style');
style.textContent = `
    .review-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
    }
    .review-modal-content {
        background: white;
        padding: 32px;
        border-radius: 16px;
        max-width: 500px;
        width: 90%;
    }
    .review-actions {
        display: flex;
        gap: 12px;
        justify-content: center;
        margin-top: 24px;
    }
`;
document.head.appendChild(style);
