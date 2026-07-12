# My Vim Setup

## Installation

```bash
# Install vim
brew install vim  # macOS
sudo apt install vim  # Ubuntu

# Install vim-plug
curl -fLo ~/.vim/autoload/plug.vim --create-dirs \
    https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
```

## Configuration

**~/.vimrc:**
```vim
" Basic settings
set number
set relativenumber
set tabstop=4
set shiftwidth=4
set expandtab
set autoindent
set smartindent

" Search settings
set hlsearch
set incsearch
set ignorecase
set smartcase

" Plugins
call plug#begin('~/.vim/plugged')
Plug 'preservim/nerdtree'
Plug 'junegunn/fzf.vim'
Plug 'tpope/vim-fugitive'
call plug#end()

" Key mappings
let mapleader = " "
nnoremap <leader>n :NERDTreeToggle<CR>
nnoremap <leader>f :Files<CR>
```

## Essential Plugins

**NERDTree:** File explorer
**fzf.vim:** Fuzzy finder
**vim-fugitive:** Git integration

## My Key Bindings

- `Space + n`: Toggle file tree
- `Space + f`: Fuzzy file search
- `Space + g`: Git status
- `jk`: Exit insert mode

## Related Documents
- [CLI Commands](../references/cli-commands.md)
- [Git Workflow](./git-workflow-guide.md)
