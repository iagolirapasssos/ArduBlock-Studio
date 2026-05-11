#!/bin/bash

listar_conteudos_find() {
    local diretorio_base="$1"
    local script_atual
    script_atual="$(basename "$0")"

    find "$diretorio_base" \
        \( \
            -path "*/node_modules" -o -path "*/node_modules/*" -o \
            -path "*/builder_script" -o -path "*/builder_script/*" -o \
            -path "*/__pycache__" -o -path "*/__pycache__/*" \
        \) -prune -o \
        -type f \
        ! -name "$script_atual" \
        ! -name "database.rules.json" \
        ! -name "package-lock.json" \
        ! -iname "*.pyc" \
        ! -iname "*.pyo" \
        ! \( \
            -iname "*.png"  -o \
            -iname "*.jpg"  -o \
            -iname "*.jpeg" -o \
            -iname "*.gif"  -o \
            -iname "*.webp" -o \
            -iname "*.svg"  -o \
            -iname "*.bmp"  -o \
            -iname "*.ico"  -o \
            -iname "*.avif" -o \
            -iname "*.css" \
        \) \
        -print | while read -r arquivo; do

        caminho_relativo="${arquivo#$diretorio_base/}"
        caminho_relativo="${caminho_relativo#./}"

        echo "$caminho_relativo:"

        if [ -r "$arquivo" ]; then
            cat "$arquivo"
        else
            echo "[Não foi possível ler o arquivo]"
        fi

        echo
        echo
    done
}

main() {
    local diretorio_base="."

    if [ $# -gt 0 ]; then
        diretorio_base="$1"
    fi

    if [ ! -d "$diretorio_base" ]; then
        echo "Erro: Diretório '$diretorio_base' não encontrado!"
        exit 1
    fi

    diretorio_base="${diretorio_base%/}"

    listar_conteudos_find "$diretorio_base"
}

main "$@"