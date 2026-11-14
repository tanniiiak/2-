"""Генерация PlantUML и локальное создание SVG."""

from typing import Dict, List


def generate_plantuml(graph: Dict[str, List[str]], start_pkg: str) -> str:
    """Генерирует текст диаграммы PlantUML."""
    lines = ["@startuml", "skinparam monochrome true"]
    
    for pkg, deps in graph.items():
        for dep in deps:
            lines.append(f'"{pkg}" --> "{dep}"')
            
    lines.append(f'"{start_pkg}"')
    lines.append("@enduml")
    
    return "\n".join(lines)


def save_plantuml(plantuml_code: str, output_file: str) -> None:
    """Сохраняет текст PlantUML в файл .puml."""
    puml_file = output_file.replace(".svg", ".puml")
    if not puml_file.endswith(".puml"):
        puml_file += ".puml"
    with open(puml_file, "w", encoding="utf-8") as f:
        f.write(plantuml_code)


def save_svg(graph: Dict[str, List[str]], output_file: str) -> None:
    """Локально генерирует простой SVG-файл с графом."""
    nodes = set()
    edges = []
    
    for pkg, deps in graph.items():
        nodes.add(pkg)
        for dep in deps:
            nodes.add(dep)
            edges.append((pkg, dep))
            
    node_list = list(nodes)
    positions = {}
    for i, node in enumerate(node_list):
        x = 50 + (i % 5) * 100
        y = 50 + (i // 5) * 100
        positions[node] = (x, y)

    svg = ['<?xml version="1.0" encoding="UTF-8"?>']
    svg.append('<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600">')
    svg.append('<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="10" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#000" /></marker></defs>')

    for src, dst in edges:
        x1, y1 = positions[src]
        x2, y2 = positions[dst]
        svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#000" marker-end="url(#arrow)" />')

    for node in node_list:
        x, y = positions[node]
        svg.append(f'<circle cx="{x}" cy="{y}" r="20" fill="#fff" stroke="#000" stroke-width="2" />')
        svg.append(f'<text x="{x}" y="{y+5}" text-anchor="middle" font-family="Arial" font-size="12">{node}</text>')

    svg.append('</svg>')
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))