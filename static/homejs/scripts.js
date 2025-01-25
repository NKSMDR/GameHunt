document.addEventListener('DOMContentLoaded', function() {
    // Original Game Cards Video Functionality
    const gameCards = document.querySelectorAll('.game-card');

    gameCards.forEach(card => {
        let hoverTimer;
        const iframe = card.querySelector('iframe');
        const unmuteButton = card.querySelector('.unmute-btn');
        const infoStrip = card.querySelector('.info-strip');

        // Store the original video URL
        const originalSrc = iframe.src;

        card.addEventListener('mouseenter', () => {
            hoverTimer = setTimeout(() => {
                card.classList.add('show-video');
                iframe.src = originalSrc;
                if (unmuteButton) {
                    unmuteButton.style.display = 'block';
                }
                if (infoStrip) {
                    infoStrip.style.opacity = '0';
                }
            }, 1000);
        });

        card.addEventListener('mouseleave', () => {
            clearTimeout(hoverTimer);
            card.classList.remove('show-video');
            iframe.src = '';
            if (unmuteButton) {
                unmuteButton.style.display = 'none';
            }
        });

        if (unmuteButton) {
            unmuteButton.addEventListener('click', (event) => {
                event.stopPropagation(); // Prevent link activation 
                if (iframe) {
                    iframe.src = iframe.src.replace('&mute=1', '');
                    unmuteButton.style.display = 'none';
                }
            });
        }
    });

    // Enhanced Game Lists Functionality
    const listContainers = document.querySelectorAll('.game-list-container');
    const scrollableLists = document.querySelectorAll('.scrollable-list');
    
    // Initialize existing scroll functionality
    scrollableLists.forEach(list => {
        // Preserve original wheel event listener
        list.addEventListener('wheel', function(e) {
            if (
                (this.scrollTop === 0 && e.deltaY < 0) || 
                (this.scrollTop + this.clientHeight === this.scrollHeight && e.deltaY > 0)
            ) {
                e.preventDefault();
            }
        });

        // Preserve original touch events
        let touchStart = 0;
        let touchEnd = 0;

        list.addEventListener('touchstart', function(e) {
            touchStart = e.changedTouches[0].screenY;
        });

        list.addEventListener('touchend', function(e) {
            touchEnd = e.changedTouches[0].screenY;
            handleSwipe.call(this);
        });

        function handleSwipe() {
            const swipeLength = touchEnd - touchStart;
            if (Math.abs(swipeLength) > 50) {
                this.scrollBy({
                    top: -swipeLength,
                    behavior: 'smooth'
                });
            }
        }
    });

    // Add new enhanced functionality to list containers
    listContainers.forEach(container => {
        const sortButtons = container.querySelectorAll('.sort-btn');
        const filterButtons = container.querySelectorAll('.filter-btn');
        const list = container.querySelector('.scrollable-list');
        const countElement = container.querySelector('.count');
        
        // Initialize item count
        if (countElement) {
            updateItemCount(list, countElement);
        }
        
        // Sorting functionality
        sortButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                const sortType = this.dataset.sort;
                const items = Array.from(list.querySelectorAll('.game-list-item'));
                
                items.sort((a, b) => {
                    const valueA = a.dataset[sortType];
                    const valueB = b.dataset[sortType];
                    
                    if (sortType === 'price') {
                        return parseFloat(valueA) - parseFloat(valueB);
                    } else if (sortType === 'rating') {
                        return parseFloat(valueB) - parseFloat(valueA);
                    }
                    return valueA.localeCompare(valueB);
                });
                
                if (this.classList.contains('sorted-asc')) {
                    items.reverse();
                    this.classList.remove('sorted-asc');
                } else {
                    this.classList.add('sorted-asc');
                }
                
                items.forEach(item => list.appendChild(item));
            });
        });
        
        // Filtering functionality
        filterButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                const filterType = this.dataset.filter;
                const items = list.querySelectorAll('.game-list-item');
                
                this.classList.toggle('active');
                const isActive = this.classList.contains('active');
                
                items.forEach(item => {
                    if (isActive) {
                        if (!item.classList.contains(filterType)) {
                            item.style.display = 'none';
                        }
                    } else {
                        item.style.display = 'flex';
                    }
                });
                
                if (countElement) {
                    updateItemCount(list, countElement);
                }
            });
        });

        // Quick view functionality
        const quickViewButtons = container.querySelectorAll('.quick-view-btn');
        const modal = document.getElementById('quickViewModal');
        
        if (modal) {
            const modalInstance = new bootstrap.Modal(modal);
            
            quickViewButtons.forEach(btn => {
                btn.addEventListener('click', function(e) {
                    e.stopPropagation();
                    const gameItem = this.closest('.game-list-item');
                    const gameData = {
                        name: gameItem.querySelector('h6').textContent,
                        price: gameItem.querySelector('.price').textContent,
                        image: gameItem.querySelector('img').src,
                        category: gameItem.querySelector('.category-badge')?.textContent || 'N/A',
                        rating: gameItem.querySelector('.rating')?.textContent || 'N/A'
                    };
                    
                    populateModal(modal, gameData);
                    modalInstance.show();
                });
            });
        }

        // Claim button functionality
        const claimButtons = container.querySelectorAll('.claim-btn');
        claimButtons.forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                const gameItem = this.closest('.game-list-item');
                const gameName = gameItem.querySelector('h6').textContent;
                
                this.innerHTML = '<i class="fas fa-check"></i> Claimed';
                this.classList.add('claimed');
                this.disabled = true;
                
                showToast(`${gameName} has been added to your library!`);
            });
        });
    });

    // Preserve original keyboard navigation
    scrollableLists.forEach(list => {
        list.tabIndex = 0;
        
        list.addEventListener('keydown', function(e) {
            switch(e.key) {
                case 'ArrowUp':
                    e.preventDefault();
                    this.scrollBy({top: -50, behavior: 'smooth'});
                    break;
                case 'ArrowDown':
                    e.preventDefault();
                    this.scrollBy({top: 50, behavior: 'smooth'});
                    break;
                case 'Home':
                    e.preventDefault();
                    this.scrollTo({top: 0, behavior: 'smooth'});
                    break;
                case 'End':
                    e.preventDefault();
                    this.scrollTo({top: this.scrollHeight, behavior: 'smooth'});
                    break;
            }
        });
    });
});

// Helper Functions
function updateItemCount(list, countElement) {
    const visibleItems = list.querySelectorAll('.game-list-item:not([style*="display: none"])').length;
    countElement.textContent = visibleItems;
}

function populateModal(modal, gameData) {
    const modalBody = modal.querySelector('.modal-body');
    modalBody.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <img src="${gameData.image}" class="img-fluid rounded" alt="${gameData.name}">
            </div>
            <div class="col-md-6">
                <h4>${gameData.name}</h4>
                <p class="badge bg-secondary">${gameData.category}</p>
                <p><i class="fas fa-star text-warning"></i> ${gameData.rating}</p>
                <p class="h5">${gameData.price}</p>
                <button class="btn btn-primary mt-3">Add to Cart</button>
            </div>
        </div>
    `;
}

function showToast(message) {
    const toastContainer = document.createElement('div');
    toastContainer.className = 'position-fixed bottom-0 end-0 p-3';
    toastContainer.style.zIndex = '11';
    
    toastContainer.innerHTML = `
        <div class="toast" role="alert">
            <div class="toast-header">
                <i class="fas fa-check-circle text-success me-2"></i>
                <strong class="me-auto">Success</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    document.body.appendChild(toastContainer);
    const toast = new bootstrap.Toast(toastContainer.querySelector('.toast'));
    toast.show();
    
    toastContainer.addEventListener('hidden.bs.toast', () => {
        document.body.removeChild(toastContainer);
    });
}