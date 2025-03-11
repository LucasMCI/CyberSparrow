#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import zipfile
import shutil
from pathlib import Path
import importlib.util
import logging

class ExtensionManager:
    def __init__(self, extensions_dir="extensions"):
        self.extensions_dir = Path(extensions_dir)
        self.extensions_dir.mkdir(exist_ok=True)
        self.installed_extensions = {}
        self.logger = logging.getLogger("ExtensionManager")
        self._load_installed_extensions()

    def _load_installed_extensions(self):
        """Carrega todas as extensões instaladas"""
        for ext_dir in self.extensions_dir.iterdir():
            if ext_dir.is_dir():
                manifest_path = ext_dir / "manifest.json"
                if manifest_path.exists():
                    try:
                        with open(manifest_path) as f:
                            manifest = json.load(f)
                            self.installed_extensions[ext_dir.name] = manifest
                    except Exception as e:
                        self.logger.error(f"Erro ao carregar extensão {ext_dir.name}: {e}")

    def install_extension(self, extension_path):
        """Instala uma nova extensão"""
        try:
            # Verificar se é um arquivo zip válido
            if not zipfile.is_zipfile(extension_path):
                raise ValueError("O arquivo não é uma extensão válida")

            with zipfile.ZipFile(extension_path) as zf:
                # Verificar manifest.json
                if "manifest.json" not in zf.namelist():
                    raise ValueError("Extensão inválida: manifest.json não encontrado")

                # Ler manifest
                manifest_data = json.loads(zf.read("manifest.json"))
                
                # Validar campos obrigatórios
                required_fields = ["name", "version", "description"]
                for field in required_fields:
                    if field not in manifest_data:
                        raise ValueError(f"Extensão inválida: campo {field} ausente no manifest.json")

                # Criar diretório para a extensão
                ext_dir = self.extensions_dir / manifest_data["name"]
                if ext_dir.exists():
                    shutil.rmtree(ext_dir)
                ext_dir.mkdir()

                # Extrair arquivos
                zf.extractall(ext_dir)

                # Adicionar ao registro de extensões instaladas
                self.installed_extensions[manifest_data["name"]] = manifest_data
                
                self.logger.info(f"Extensão {manifest_data['name']} instalada com sucesso")
                return True

        except Exception as e:
            self.logger.error(f"Erro ao instalar extensão: {e}")
            return False

    def uninstall_extension(self, extension_name):
        """Remove uma extensão instalada"""
        try:
            if extension_name in self.installed_extensions:
                ext_dir = self.extensions_dir / extension_name
                if ext_dir.exists():
                    shutil.rmtree(ext_dir)
                del self.installed_extensions[extension_name]
                self.logger.info(f"Extensão {extension_name} removida com sucesso")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Erro ao remover extensão {extension_name}: {e}")
            return False

    def get_installed_extensions(self):
        """Retorna lista de extensões instaladas"""
        return self.installed_extensions

    def enable_extension(self, extension_name):
        """Ativa uma extensão"""
        if extension_name in self.installed_extensions:
            manifest = self.installed_extensions[extension_name]
            manifest["enabled"] = True
            self._save_manifest(extension_name, manifest)
            return True
        return False

    def disable_extension(self, extension_name):
        """Desativa uma extensão"""
        if extension_name in self.installed_extensions:
            manifest = self.installed_extensions[extension_name]
            manifest["enabled"] = False
            self._save_manifest(extension_name, manifest)
            return True
        return False

    def _save_manifest(self, extension_name, manifest):
        """Salva alterações no manifest.json de uma extensão"""
        manifest_path = self.extensions_dir / extension_name / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=4)
        self.installed_extensions[extension_name] = manifest

    def load_extension_script(self, extension_name):
        """Carrega o script principal de uma extensão"""
        if extension_name not in self.installed_extensions:
            return None

        manifest = self.installed_extensions[extension_name]
        if "main_script" not in manifest:
            return None

        script_path = self.extensions_dir / extension_name / manifest["main_script"]
        if not script_path.exists():
            return None

        try:
            spec = importlib.util.spec_from_file_location(
                f"extension_{extension_name}", script_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            self.logger.error(f"Erro ao carregar script da extensão {extension_name}: {e}")
            return None 