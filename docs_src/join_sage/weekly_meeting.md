# 周会安排

<div id="weekly-schedule-container">
    <div class="controls">
        <button id="reset-all" onclick="scheduler.resetAll()">重置所有</button>
    </div>
    
    <!-- 周期信息显示 -->
    <div class="cycle-info">
        <span>当前周期: <strong id="current-cycle">1</strong></span>
        <span>本周日期: <strong id="current-week-date">加载中...</strong></span>
    </div>
    
    <!-- 上方两个区域 - 并排显示 -->
    <div class="presenters-sections">
        <div class="presenters-column">
            <h3>本周汇报人员</h3>
            <div id="current-presenters" class="drop-zone current-week-zone">
                <div class="zone-hint">本周汇报人员</div>
            </div>
        </div>
        
        <div class="presenters-column">
            <h3>下周准备汇报人员</h3>
            <div id="next-presenters" class="drop-zone next-week-zone">
                <div class="zone-hint">下周准备汇报人员</div>
            </div>
        </div>
    </div>

    <!-- 下方两个区域 - 并排显示 -->
    <div class="members-sections">
        <div class="members-column">
            <h3>已汇报成员 (本周期)</h3>
            <div id="presented-members" class="drop-zone presented-zone">
                <div class="zone-hint">已汇报的成员</div>
            </div>
        </div>
        
        <div class="members-column">
            <h3>待汇报成员</h3>
            <div id="pending-members" class="drop-zone pending-zone">
                <div class="zone-hint">待汇报的成员</div>
            </div>
        </div>
    </div>
</div>

<style>
#weekly-schedule-container {
    max-width: 1200px;
    margin: 20px auto;
    padding: 20px;
    font-family: 'Public Sans', sans-serif;
    background: #f8f9fa;
    border-radius: 12px;
}

.controls-section {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    padding: 15px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.controls {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
    padding: 15px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    justify-content: flex-start;
}

.controls button {
    padding: 10px 16px;
    background: #007acc;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    transition: all 0.2s ease;
}

.controls button:hover {
    background: #005a9e;
    transform: translateY(-1px);
}

.week-controls {
    display: flex;
    gap: 10px;
}

.week-controls button {
    padding: 10px 16px;
    background: #007acc;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    transition: all 0.2s ease;
}

.week-controls button:hover {
    background: #005a9e;
    transform: translateY(-1px);
}

.cycle-info {
    display: flex;
    gap: 20px;
    color: #666;
    font-size: 14px;
}

.cycle-info span {
    padding: 5px 10px;
    background: #e3f2fd;
    border-radius: 4px;
}

/* 上方两个区域 - 并排显示 */
.presenters-sections {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 30px;
}

.presenters-column h3 {
    margin-bottom: 15px;
    color: #333;
    font-size: 16px;
}

.current-week-zone {
    min-height: 180px;
    background: linear-gradient(135deg, #e8f5e8, #f1f8e9);
    border: 3px dashed #4caf50;
    border-radius: 12px;
    position: relative;
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    padding: 20px;
    align-items: flex-start;
    align-content: flex-start;
}

.next-week-zone {
    min-height: 180px;
    background: linear-gradient(135deg, #e1f5fe, #f3e5f5);
    border: 3px dashed #00bcd4;
    border-radius: 12px;
    position: relative;
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    padding: 20px;
    align-items: flex-start;
    align-content: flex-start;
}

/* 下方两个区域 */
.members-sections {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}

.members-column h3 {
    margin-bottom: 15px;
    color: #333;
    font-size: 16px;
}

.presented-zone {
    min-height: 300px;
    background: linear-gradient(135deg, #fff3e0, #fef7ed);
    border: 2px dashed #ff9800;
    border-radius: 8px;
    padding: 15px;
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    align-items: flex-start;
    align-content: flex-start;
}

.pending-zone {
    min-height: 300px;
    background: linear-gradient(135deg, #e3f2fd, #f3e5f5);
    border: 2px dashed #2196f3;
    border-radius: 8px;
    padding: 15px;
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    align-items: flex-start;
    align-content: flex-start;
}

.drop-zone {
    transition: all 0.3s ease;
    position: relative;
}

.drop-zone.drag-over {
    transform: scale(1.02);
    box-shadow: 0 8px 16px rgba(0,0,0,0.15);
}

.current-week-zone.drag-over {
    border-color: #2e7d32;
    background: linear-gradient(135deg, #c8e6c9, #dcedc8);
}

.next-week-zone.drag-over {
    border-color: #0097a7;
    background: linear-gradient(135deg, #b2ebf2, #e1bee7);
}

.presented-zone.drag-over {
    border-color: #f57c00;
    background: linear-gradient(135deg, #ffe0b2, #fff3e0);
}

.pending-zone.drag-over {
    border-color: #1976d2;
    background: linear-gradient(135deg, #bbdefb, #e1bee7);
}

.zone-hint {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: #999;
    font-style: italic;
    font-size: 14px;
    pointer-events: none;
    opacity: 0.7;
}

.zone-hint.hidden {
    display: none;
}

.current-week-zone .zone-hint {
    color: #4caf50;
}

.next-week-zone .zone-hint {
    color: #00bcd4;
}

/* 成员卡片样式 */
.member-card {
    background: white;
    padding: 12px 16px;
    border-radius: 8px;
    cursor: grab;
    user-select: none;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 120px;
    position: relative;
}

.member-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.member-card.dragging {
    opacity: 0.8;
    transform: rotate(5deg);
    cursor: grabbing;
    z-index: 1000;
}

.member-card .name {
    font-weight: 500;
    color: #333;
}

.member-card .status {
    font-size: 10px;
    padding: 2px 6px;
    border-radius: 10px;
    color: white;
    font-weight: 500;
}

.member-card .status.current {
    background: #4caf50;
}

.member-card .status.next {
    background: #00bcd4;
}

.member-card .status.presented {
    background: #ff9800;
}

.member-card .status.pending {
    background: #2196f3;
}

.member-card .last-date {
    font-size: 11px;
    color: #666;
    margin-left: auto;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .controls-section {
        flex-direction: column;
        gap: 15px;
        align-items: stretch;
    }
    
    .week-controls {
        justify-content: center;
    }
    
    .cycle-info {
        justify-content: center;
    }
    
    .presenters-sections,
    .members-sections {
        grid-template-columns: 1fr;
        gap: 15px;
    }
    
    .current-week-zone,
    .next-week-zone {
        min-height: 100px;
        padding: 15px;
    }
    
    .presented-zone,
    .pending-zone {
        min-height: 150px;
    }
}

/* 动画效果 */
@keyframes memberDrop {
    0% { transform: scale(1.1); }
    100% { transform: scale(1); }
}

.member-card.dropped {
    animation: memberDrop 0.3s ease;
}

/* 空状态样式 */
.empty-zone .zone-hint {
    opacity: 1;
}

.non-empty-zone .zone-hint {
    display: none;
}
</style>

<script>
class DragDropScheduler {
    constructor() {
        // 先检查是否有存储的数据，如果没有或者成员数量不对，使用默认成员
        const storedMembers = this.loadData('dragScheduler_members');
        if (!storedMembers || storedMembers.length !== 20) {
            console.log('Loading default members...');
            this.members = this.getDefaultMembers();
            this.currentCycle = 1;
            this.weekHistory = [];
            this.currentWeekPresenters = [];
            this.nextWeekPresenters = [];
        } else {
            console.log('Loading stored members...', storedMembers.length);
            this.members = storedMembers;
            this.currentCycle = this.loadData('dragScheduler_cycle') || 1;
            this.weekHistory = this.loadData('dragScheduler_history') || [];
            this.currentWeekPresenters = this.loadData('dragScheduler_currentWeek') || [];
            this.nextWeekPresenters = this.loadData('dragScheduler_nextWeek') || [];
        }
        
        console.log('Total members loaded:', this.members.length);
        this.init();
    }
    
    getDefaultMembers() {
        return [
            { id: 1, name: 'Hongru', lastPresented: null, cycleCount: 0 },
            { id: 2, name: 'Mingqi', lastPresented: null, cycleCount: 0 },
            { id: 3, name: 'Ruicheng', lastPresented: null, cycleCount: 0 },
            { id: 4, name: 'Ruipeng', lastPresented: null, cycleCount: 0 },
            { id: 5, name: 'Xinyan', lastPresented: null, cycleCount: 0 },
            { id: 6, name: 'Ziao', lastPresented: null, cycleCount: 0 },
            { id: 7, name: 'Senlei', lastPresented: null, cycleCount: 0 },
            { id: 8, name: 'Xincai', lastPresented: null, cycleCount: 0 },
            { id: 9, name: 'Liujun', lastPresented: null, cycleCount: 0 },
            { id: 10, name: 'Yanbo', lastPresented: null, cycleCount: 0 },
            { id: 11, name: 'Jinyun', lastPresented: null, cycleCount: 0 },
            { id: 12, name: 'Jingyuan', lastPresented: null, cycleCount: 0 },
            { id: 13, name: 'Peilin', lastPresented: null, cycleCount: 0 },
            { id: 14, name: 'Xiaohan', lastPresented: null, cycleCount: 0 },
            { id: 15, name: 'Changwu', lastPresented: null, cycleCount: 0 }
        ];
    }
    
    init() {
        this.updateCycleInfo();
        this.initializeSchedule();
        this.renderMembers();
        this.setupDragAndDrop();
        
        // 首次加载时保存数据，确保新的默认成员被保存
        this.saveAllData();
    }
    
    initializeSchedule() {
        // 如果当前周没有安排，自动安排
        if (this.currentWeekPresenters.length === 0) {
            this.autoFillCurrentWeek();
        }
        
        // 如果下周没有安排，自动安排
        if (this.nextWeekPresenters.length === 0) {
            this.autoFillNextWeek();
        }
    }
    
    loadData(key) {
        try {
            const data = localStorage.getItem(key);
            return data ? JSON.parse(data) : null;
        } catch (e) {
            return null;
        }
    }
    
    saveData(key, data) {
        try {
            localStorage.setItem(key, JSON.stringify(data));
        } catch (e) {
            console.error('Failed to save data:', e);
        }
    }
    
    saveAllData() {
        this.saveData('dragScheduler_members', this.members);
        this.saveData('dragScheduler_cycle', this.currentCycle);
        this.saveData('dragScheduler_history', this.weekHistory);
        this.saveData('dragScheduler_currentWeek', this.currentWeekPresenters);
        this.saveData('dragScheduler_nextWeek', this.nextWeekPresenters);
    }
    
    updateCycleInfo() {
        const cycleElement = document.getElementById('current-cycle');
        if (cycleElement) {
            cycleElement.textContent = this.currentCycle;
        }
        
        const today = new Date();
        const weekStart = this.getWeekStart(today);
        const weekEnd = new Date(weekStart);
        weekEnd.setDate(weekStart.getDate() + 6);
        
        const formatDate = (date) => `${date.getMonth() + 1}/${date.getDate()}`;
        const weekDateElement = document.getElementById('current-week-date');
        if (weekDateElement) {
            weekDateElement.textContent = `${formatDate(weekStart)} - ${formatDate(weekEnd)}`;
        }
    }
    
    getWeekStart(date) {
        const d = new Date(date);
        const day = d.getDay();
        const diff = d.getDate() - day + (day === 0 ? -6 : 1);
        return new Date(d.setDate(diff));
    }
    
    getMemberStatus(member) {
        if (this.currentWeekPresenters.includes(member.id)) {
            return 'current';
        } else if (this.nextWeekPresenters.includes(member.id)) {
            return 'next';
        } else if (member.cycleCount === this.currentCycle) {
            return 'presented';
        } else {
            return 'pending';
        }
    }
    
    getMemberZone(member) {
        const status = this.getMemberStatus(member);
        if (status === 'current') return 'current-presenters';
        if (status === 'next') return 'next-presenters';
        if (status === 'presented') return 'presented-members';
        return 'pending-members';
    }
    
    renderMembers() {
        // 清空所有区域
        document.getElementById('current-presenters').innerHTML = '';
        document.getElementById('next-presenters').innerHTML = '';
        document.getElementById('presented-members').innerHTML = '';
        document.getElementById('pending-members').innerHTML = '';
        
        // 渲染每个成员到对应区域
        this.members.forEach(member => {
            const card = this.createMemberCard(member);
            const zoneId = this.getMemberZone(member);
            document.getElementById(zoneId).appendChild(card);
        });
        
        // 更新提示文本
        this.updateZoneHints();
    }
    
    createMemberCard(member) {
        const card = document.createElement('div');
        card.className = 'member-card';
        card.draggable = true;
        card.dataset.memberId = member.id;
        
        const status = this.getMemberStatus(member);
        const statusText = {
            'current': '本周',
            'next': '下周',
            'presented': '已报',
            'pending': '待报'
        };
        
        const lastDate = member.lastPresented ? 
            new Date(member.lastPresented).toLocaleDateString('zh-CN', {month: 'short', day: 'numeric'}) : 
            '';
        
        card.innerHTML = `
            <span class="name">${member.name}</span>
            <span class="status ${status}">${statusText[status]}</span>
            ${lastDate ? `<span class="last-date">${lastDate}</span>` : ''}
        `;
        
        return card;
    }
    
    updateZoneHints() {
        const zones = [
            { id: 'current-presenters', hint: '本周汇报人员' },
            { id: 'next-presenters', hint: '下周准备汇报人员' },
            { id: 'presented-members', hint: '本周期已汇报的成员' },
            { id: 'pending-members', hint: '待汇报的成员' }
        ];
        
        zones.forEach(zone => {
            const element = document.getElementById(zone.id);
            const hasMembers = element.querySelector('.member-card');
            
            if (!hasMembers) {
                if (!element.querySelector('.zone-hint')) {
                    const hint = document.createElement('div');
                    hint.className = 'zone-hint';
                    hint.textContent = zone.hint;
                    element.appendChild(hint);
                }
                element.classList.add('empty-zone');
                element.classList.remove('non-empty-zone');
            } else {
                const hint = element.querySelector('.zone-hint');
                if (hint) hint.remove();
                element.classList.add('non-empty-zone');
                element.classList.remove('empty-zone');
            }
        });
    }
    
    setupDragAndDrop() {
        const container = document.getElementById('weekly-schedule-container');
        
        // 设置拖拽事件
        container.addEventListener('dragstart', (e) => {
            if (e.target.classList.contains('member-card')) {
                e.target.classList.add('dragging');
                e.dataTransfer.setData('text/plain', e.target.dataset.memberId);
                e.dataTransfer.effectAllowed = 'move';
            }
        });
        
        container.addEventListener('dragend', (e) => {
            if (e.target.classList.contains('member-card')) {
                e.target.classList.remove('dragging');
            }
        });
        
        // 设置放置区域事件
        const dropZones = ['current-presenters', 'next-presenters', 'presented-members', 'pending-members'];
        
        dropZones.forEach(zoneId => {
            const zone = document.getElementById(zoneId);
            
            zone.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'move';
                zone.classList.add('drag-over');
            });
            
            zone.addEventListener('dragleave', (e) => {
                if (!zone.contains(e.relatedTarget)) {
                    zone.classList.remove('drag-over');
                }
            });
            
            zone.addEventListener('drop', (e) => {
                e.preventDefault();
                zone.classList.remove('drag-over');
                
                const memberId = parseInt(e.dataTransfer.getData('text/plain'));
                const member = this.members.find(m => m.id === memberId);
                
                if (member) {
                    this.moveMemberToZone(member, zoneId);
                }
            });
        });
    }
    
    moveMemberToZone(member, targetZoneId) {
        const today = new Date();
        const oldStatus = this.getMemberStatus(member);
        
        // 先从所有列表中移除该成员
        this.currentWeekPresenters = this.currentWeekPresenters.filter(id => id !== member.id);
        this.nextWeekPresenters = this.nextWeekPresenters.filter(id => id !== member.id);
        
        // 根据目标区域更新成员状态
        if (targetZoneId === 'current-presenters') {
            this.currentWeekPresenters.push(member.id);
        } else if (targetZoneId === 'next-presenters') {
            this.nextWeekPresenters.push(member.id);
        } else if (targetZoneId === 'presented-members') {
            // 标记为已汇报
            member.lastPresented = today.toISOString();
            member.cycleCount = this.currentCycle;
        }
        // pending-members 不需要特殊处理，保持原状态
        
        // 执行智能填充逻辑
        this.autoFillLogic();
        
        this.saveAllData();
        this.renderMembers();
        
        // 添加动画效果
        setTimeout(() => {
            const card = document.querySelector(`[data-member-id="${member.id}"]`);
            if (card) {
                card.classList.add('dropped');
                setTimeout(() => card.classList.remove('dropped'), 300);
            }
        }, 50);
    }
    
    autoFillLogic() {
        // 确保本周汇报人员至少有2人
        while (this.currentWeekPresenters.length < 2) {
            let filled = false;
            
            // 1. 先从下周汇报中选择
            if (this.nextWeekPresenters.length > 0) {
                const randomIndex = Math.floor(Math.random() * this.nextWeekPresenters.length);
                const selectedId = this.nextWeekPresenters[randomIndex];
                this.nextWeekPresenters.splice(randomIndex, 1);
                this.currentWeekPresenters.push(selectedId);
                filled = true;
            }
            
            if (!filled) {
                // 2. 从待汇报成员中选择
                const pendingMembers = this.getPendingMembers();
                if (pendingMembers.length > 0) {
                    const selectedMember = this.selectBestMember(pendingMembers);
                    this.currentWeekPresenters.push(selectedMember.id);
                    filled = true;
                }
            }
            
            if (!filled) {
                // 3. 从已汇报成员的最下方选择
                const presentedMembers = this.getPresentedMembers();
                if (presentedMembers.length > 0) {
                    const lastMember = presentedMembers[presentedMembers.length - 1];
                    this.currentWeekPresenters.push(lastMember.id);
                    // 重置该成员的状态
                    lastMember.cycleCount = 0;
                    lastMember.lastPresented = null;
                    filled = true;
                }
            }
            
            if (!filled) break; // 防止无限循环
        }
        
        // 确保下周汇报人员至少有2人
        while (this.nextWeekPresenters.length < 2) {
            let filled = false;
            
            // 从待汇报成员中选择
            const pendingMembers = this.getPendingMembers();
            if (pendingMembers.length > 0) {
                const selectedMember = this.selectBestMember(pendingMembers);
                this.nextWeekPresenters.push(selectedMember.id);
                filled = true;
            } else {
                // 从已汇报成员的最下方选择
                const presentedMembers = this.getPresentedMembers();
                if (presentedMembers.length > 0) {
                    const lastMember = presentedMembers[presentedMembers.length - 1];
                    this.nextWeekPresenters.push(lastMember.id);
                    // 重置该成员的状态
                    lastMember.cycleCount = 0;
                    lastMember.lastPresented = null;
                    filled = true;
                }
            }
            
            if (!filled) break; // 防止无限循环
        }
    }
    
    autoFillCurrentWeek() {
        const pendingMembers = this.getPendingMembers();
        const selectedMembers = pendingMembers.slice(0, 2).map(m => m.id);
        this.currentWeekPresenters = selectedMembers;
    }
    
    autoFillNextWeek() {
        const pendingMembers = this.getPendingMembers().filter(m => 
            !this.currentWeekPresenters.includes(m.id)
        );
        const selectedMembers = pendingMembers.slice(0, 2).map(m => m.id);
        this.nextWeekPresenters = selectedMembers;
    }
    
    getPendingMembers() {
        return this.members.filter(m => 
            m.cycleCount !== this.currentCycle && 
            !this.currentWeekPresenters.includes(m.id) && 
            !this.nextWeekPresenters.includes(m.id)
        ).sort((a, b) => {
            if (!a.lastPresented && !b.lastPresented) return 0;
            if (!a.lastPresented) return -1;
            if (!b.lastPresented) return 1;
            return new Date(a.lastPresented) - new Date(b.lastPresented);
        });
    }
    
    getPresentedMembers() {
        return this.members.filter(m => 
            m.cycleCount === this.currentCycle &&
            !this.currentWeekPresenters.includes(m.id) && 
            !this.nextWeekPresenters.includes(m.id)
        ).sort((a, b) => {
            if (!a.lastPresented && !b.lastPresented) return 0;
            if (!a.lastPresented) return -1;
            if (!b.lastPresented) return 1;
            return new Date(a.lastPresented) - new Date(b.lastPresented);
        });
    }
    
    selectBestMember(members) {
        return members[0]; // 已经按优先级排序，选择第一个
    }
    
    resetAll() {
        // 清除所有本地存储数据
        localStorage.removeItem('dragScheduler_members');
        localStorage.removeItem('dragScheduler_cycle');
        localStorage.removeItem('dragScheduler_history');
        localStorage.removeItem('dragScheduler_currentWeek');
        localStorage.removeItem('dragScheduler_nextWeek');
        
        // 重新初始化
        this.members = this.getDefaultMembers();
        this.currentCycle = 1;
        this.currentWeekPresenters = [];
        this.nextWeekPresenters = [];
        
        // 重新初始化排班
        this.initializeSchedule();
        
        // 保存初始状态并重新渲染
        this.saveAllData();
        this.renderMembers();
        this.updateCycleInfo();
        
        console.log('系统已重置');
    }
    
    autoSchedule() {
        // 重新初始化排班
        this.currentWeekPresenters = [];
        this.nextWeekPresenters = [];
        
        this.autoFillCurrentWeek();
        this.autoFillNextWeek();
        
        this.saveAllData();
        this.renderMembers();
        
        const currentNames = this.currentWeekPresenters.map(id => {
            const member = this.members.find(m => m.id === id);
            return member ? member.name : '';
        }).filter(name => name);
        
        const nextNames = this.nextWeekPresenters.map(id => {
            const member = this.members.find(m => m.id === id);
            return member ? member.name : '';
        }).filter(name => name);
        
        alert(`已自动安排:\n本周汇报: ${currentNames.join(', ')}\n下周准备: ${nextNames.join(', ')}`);
    }
    
    saveSchedule() {
        if (this.currentWeekPresenters.length === 0) {
            alert('请先安排本周汇报人员');
            return;
        }
        
        const today = new Date();
        const weekStart = this.getWeekStart(today);
        
        // 将当前安排保存到历史
        const weekRecord = {
            week: this.formatWeek(weekStart),
            date: weekStart.toISOString(),
            presenters: this.currentWeekPresenters.map(id => {
                const member = this.members.find(m => m.id === id);
                return member ? member.name : '';
            }).filter(name => name),
            cycle: this.currentCycle
        };
        
        this.weekHistory.unshift(weekRecord);
        
        // 更新汇报成员的状态
        this.currentWeekPresenters.forEach(memberId => {
            const member = this.members.find(m => m.id === memberId);
            if (member) {
                member.lastPresented = today.toISOString();
                member.cycleCount = this.currentCycle;
            }
        });
        
        // 下周的成员变成本周的成员
        this.currentWeekPresenters = [...this.nextWeekPresenters];
        this.nextWeekPresenters = [];
        
        // 自动安排下周
        this.autoFillNextWeek();
        
        // 检查是否需要开始新周期
        const allPresented = this.members.every(m => m.cycleCount === this.currentCycle);
        if (allPresented) {
            this.startNewCycle();
        }
        
        this.saveAllData();
        this.renderMembers();
        this.updateCycleInfo();
        
        alert('本周排班已保存，下周人员已自动安排！');
    }
    
    startNewCycle() {
        this.currentCycle++;
        this.updateCycleInfo();
        alert(`开始新周期 ${this.currentCycle}！`);
    }
    
    resetSchedule() {
        if (!confirm('确定要重置所有数据吗？此操作不可恢复！\n所有成员将回到待汇报状态，并自动安排本周和下周汇报人员。')) {
            return;
        }
        
        // 重置所有成员数据
        this.members = this.getDefaultMembers();
        this.currentCycle = 1;
        this.weekHistory = [];
        this.currentWeekPresenters = [];
        this.nextWeekPresenters = [];
        
        // 自动安排本周和下周汇报人员
        this.autoFillCurrentWeek();
        this.autoFillNextWeek();
        
        this.saveAllData();
        this.updateCycleInfo();
        this.renderMembers();
        
        alert('所有数据已重置！\n所有成员已回到待汇报状态，并自动安排了本周和下周的汇报人员。');
    }
    
    formatWeek(startDate) {
        const endDate = new Date(startDate);
        endDate.setDate(startDate.getDate() + 6);
        
        const formatDate = (date) => `${date.getMonth() + 1}/${date.getDate()}`;
        return `${formatDate(startDate)} - ${formatDate(endDate)}`;
    }
}

// 全局实例
let scheduler;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    scheduler = new DragDropScheduler();
});

// 全局函数
function saveSchedule() {
    scheduler.saveSchedule();
}

function autoSchedule() {
    scheduler.autoSchedule();
}

function resetSchedule() {
    scheduler.resetSchedule();
}
</script>
