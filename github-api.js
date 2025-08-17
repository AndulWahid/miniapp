// GitHub API Integration for direct JSON file updates
class GitHubAPI {
    constructor(token, owner, repo, branch = 'main') {
        this.token = token;
        this.owner = owner;
        this.repo = repo;
        this.branch = branch;
        this.baseURL = 'https://api.github.com';
    }

    // Get file content and SHA (needed for updates)
    async getFileInfo(path) {
        try {
            const response = await fetch(`${this.baseURL}/repos/${this.owner}/${this.repo}/contents/${path}`, {
                headers: {
                    'Authorization': `token ${this.token}`,
                    'Accept': 'application/vnd.github.v3+json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                return {
                    sha: data.sha,
                    content: atob(data.content) // Decode base64 content
                };
            } else if (response.status === 404) {
                // File doesn't exist yet
                return { sha: null, content: null };
            } else {
                throw new Error(`GitHub API error: ${response.status}`);
            }
        } catch (error) {
            console.error('Error getting file info:', error);
            throw error;
        }
    }

    // Update or create a file
    async updateFile(path, content, message = 'Update via web interface') {
        try {
            // Get current file info
            const fileInfo = await this.getFileInfo(path);
            
            const body = {
                message: message,
                content: btoa(content), // Encode to base64
                branch: this.branch
            };

            // If file exists, include SHA for update
            if (fileInfo.sha) {
                body.sha = fileInfo.sha;
            }

            const response = await fetch(`${this.baseURL}/repos/${this.owner}/${this.repo}/contents/${path}`, {
                method: 'PUT',
                headers: {
                    'Authorization': `token ${this.token}`,
                    'Accept': 'application/vnd.github.v3+json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(body)
            });

            if (response.ok) {
                const data = await response.json();
                return {
                    success: true,
                    commit: data.commit,
                    content: data.content
                };
            } else {
                const errorData = await response.json();
                throw new Error(`GitHub API error: ${errorData.message || response.status}`);
            }
        } catch (error) {
            console.error('Error updating file:', error);
            throw error;
        }
    }

    // Update custom filters
    async updateCustomFilters(filters) {
        const content = JSON.stringify(filters, null, 2);
        return await this.updateFile(
            'src/booked_slots/custom_filters.json',
            content,
            'Update custom filters via web interface'
        );
    }

    // Update booked slots
    async updateBookedSlots(slots) {
        const content = JSON.stringify(slots, null, 2);
        return await this.updateFile(
            'src/booked_slots/booked_slots.json',
            content,
            'Update booked slots via web interface'
        );
    }

    // Get current custom filters
    async getCustomFilters() {
        try {
            const fileInfo = await this.getFileInfo('src/booked_slots/custom_filters.json');
            if (fileInfo.content) {
                return JSON.parse(fileInfo.content);
            }
            return null;
        } catch (error) {
            console.error('Error getting custom filters:', error);
            return null;
        }
    }

    // Get current booked slots
    async getBookedSlots() {
        try {
            const fileInfo = await this.getFileInfo('src/booked_slots/booked_slots.json');
            if (fileInfo.content) {
                return JSON.parse(fileInfo.content);
            }
            return [];
        } catch (error) {
            console.error('Error getting booked slots:', error);
            return [];
        }
    }

    // Delete a specific slot by ID
    async deleteSlot(slotId) {
        try {
            const currentSlots = await this.getBookedSlots();
            const updatedSlots = currentSlots.filter(slot => slot.id !== slotId);
            await this.updateBookedSlots(updatedSlots);
            return { success: true };
        } catch (error) {
            console.error('Error deleting slot:', error);
            throw error;
        }
    }

    // Update a specific slot
    async updateSlot(slotId, updatedSlot) {
        try {
            const currentSlots = await this.getBookedSlots();
            const slotIndex = currentSlots.findIndex(slot => slot.id === slotId);
            
            if (slotIndex === -1) {
                throw new Error('Slot not found');
            }
            
            // Preserve the ID and update other fields
            currentSlots[slotIndex] = {
                ...currentSlots[slotIndex],
                ...updatedSlot,
                id: slotId
            };
            
            await this.updateBookedSlots(currentSlots);
            return { success: true, slot: currentSlots[slotIndex] };
        } catch (error) {
            console.error('Error updating slot:', error);
            throw error;
        }
    }
}

// Global GitHub API instance
let githubAPI = null;

// Initialize GitHub API
function initGitHubAPI(token, owner, repo, branch = 'main') {
    try {
        githubAPI = new GitHubAPI(token, owner, repo, branch);
        window.githubAPI = githubAPI; // Ensure it's set on window
        console.log('GitHub API initialized successfully');
        return githubAPI;
    } catch (error) {
        console.error('Failed to initialize GitHub API:', error);
        return null;
    }
}

// Export for use in other files
window.GitHubAPI = GitHubAPI;
window.initGitHubAPI = initGitHubAPI;
window.githubAPI = githubAPI; 
