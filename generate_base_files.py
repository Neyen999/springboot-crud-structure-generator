import os

def pascal_to_snake(name):
    result = [name[0].lower()]  # Convierte la primera letra a minúscula
    for char in name[1:]:
        if char.isupper():
            result.append('_')
            result.append(char.lower())  # Agrega un guion bajo y la letra en minúscula
        else:
            result.append(char)
    return ''.join(result)

def find_src_main_java_com(base_path):
    target_path = os.path.join('src', 'main', 'java', 'com')
    for root, dirs, files in os.walk(base_path):
        if target_path in root:
            sub_dirs = root[len(base_path) + len(target_path) + 1:].split(os.sep)
            if len(sub_dirs) >= 3:
                return root
    return None

def generate_files(entity_name, base_path):
    entity_name_lower = entity_name.lower()
    table_name = pascal_to_snake(entity_name) + "s"

    print(f"El nombre de la tabla es: {table_name}")
    # Plantillas de código
    templates = {
        'models': """
package {package}.models;

import jakarta.persistence.*;

@Entity
@Table(name = "{tableName}")
public class {EntityName} {
    @Id
    private Long id;
    // Otros campos...
}
""",
        'repositories': """
package {package}.repositories;

import {package}.models.{EntityName};
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface {EntityName}Repository extends JpaRepository<{EntityName}, Long> {
}
""",
        'services': """
package {package}.services;

import {package}.models.{EntityName};
import {package}.repositories.{EntityName}Repository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class {EntityName}Service {

    @Autowired
    private {EntityName}Repository repository;

    public List<{EntityName}> findAll() {
        return repository.findAll();
    }

    public {EntityName} findById(Long id) {
        return repository.findById(id).orElse(null);
    }

    public {EntityName} save({EntityName} entity) {
        return repository.save(entity);
    }

    public void deleteById(Long id) {
        repository.deleteById(id);
    }
}
""",
        'controllers': """
package {package}.controllers;

import {package}.models.{EntityName};
import {package}.services.{EntityName}Service;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/{entityName}")
public class {EntityName}Controller {

    @Autowired
    private {EntityName}Service service;

    @GetMapping
    public List<{EntityName}> getAll() {
        return service.findAll();
    }

    @GetMapping("/{id}")
    public {EntityName} getById(@PathVariable Long id) {
        return service.findById(id);
    }

    @PostMapping
    public {EntityName} create(@RequestBody {EntityName} entity) {
        return service.save(entity);
    }

    @DeleteMapping("/{id}")
    public void delete(@PathVariable Long id) {
        service.deleteById(id);
    }
}
"""
    }

    # Encontrar el directorio src/main/java/{organizacion}/{aplicacion}
    src_main_java_com_path = find_src_main_java_com(base_path)

    if src_main_java_com_path is None:
        print("No se encontró el directorio 'src/main/java/'. Asegúrate de estar en el directorio correcto.")
        return

    # Extraer el paquete base
    print(f"El directorio encontrado: {src_main_java_com_path}")
    package_base = src_main_java_com_path.split(os.path.join('src', 'main', 'java') + os.sep)[1].replace(os.sep, '.')

    print(f"El package base es: {package_base}")

    package_parts = package_base.split('.')

    # Crear directorios necesarios
    entity_dir = os.path.join(src_main_java_com_path, 'models')
    repository_dir = os.path.join(src_main_java_com_path, 'repositories')
    service_dir = os.path.join(src_main_java_com_path, 'services')
    controller_dir = os.path.join(src_main_java_com_path, 'controllers')

    os.makedirs(entity_dir, exist_ok=True)
    os.makedirs(repository_dir, exist_ok=True)
    os.makedirs(service_dir, exist_ok=True)
    os.makedirs(controller_dir, exist_ok=True)

     # Generar archivos a partir de plantillas
    for key, template in templates.items():
        content = template.replace("{EntityName}", entity_name).replace("{entityName}", entity_name_lower).replace("{package}", package_base).replace("{tableName}", table_name)
        if key == "repositories":
            file_name = f'{entity_name}Repository.java'
        elif key == "models":
            file_name = f'{entity_name}.java'  # No agrega el sufijo "Model"
        else:
            file_name = f'{entity_name}{key[:-1].capitalize()}.java'  # Cambia esto para quitar la 's' final
        file_path = os.path.join(src_main_java_com_path, key, file_name)

        print(f"El file name es: {file_name}")
        print(f"El file path es: {file_path}")
        with open(file_path, 'w') as f:
            f.write(content)

    print("Archivos generados con éxito.")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generar archivos de entidad, repositorio, servicio y controlador en un proyecto Spring Boot.")
    parser.add_argument("entity_names", nargs='+', help="El nombre de la(s) entidad(es) a crear")

    args = parser.parse_args()

    # Obtener el directorio actual
    current_directory = os.getcwd()
    print(f"Directorio actual: {current_directory}")
#     generate_files(args.entity_name, current_directory)
    for entity_name in args.entity_names:
        generate_files(entity_name, current_directory)