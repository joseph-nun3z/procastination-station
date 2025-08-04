# Multi-Language Setup Guide / Guia de Configuração Multi-Idioma

## How to Use / Como Usar

### Language Structure / Estrutura de Idiomas
- **EN/** - English content / Conteúdo em inglês
- **PT/** - Portuguese content / Conteúdo em português  
- **Shared/** - Language-neutral content (maps, images) / Conteúdo neutro (mapas, imagens)

### Switching Languages / Alternar Idiomas
1. Use the language links at the top of Home pages / Use os links de idioma no topo das páginas iniciais
2. **English**: Start from [[Home]] / **Português**: Comece em [[Home-PT]]

### Cross-Language Linking / Links Entre Idiomas
Each page should include a link to its translation:
Cada página deve incluir um link para sua tradução:

```markdown
**Versão PT:** [[PT/path/to/page]] 
**EN Version:** [[EN/path/to/page]]
```

### Best Practices / Melhores Práticas

#### For Content Creators / Para Criadores de Conteúdo
- Create content in your preferred language first / Crie conteúdo no seu idioma preferido primeiro
- Add cross-language links when translations exist / Adicione links entre idiomas quando traduções existirem
- Use Shared/ folder for maps and images / Use a pasta Shared/ para mapas e imagens

#### Template Usage / Uso de Templates
- **English**: Use templates in `EN/Templates/`
- **Português**: Use templates em `PT/Templates/`

#### Shared Resources / Recursos Compartilhados
- Maps, battle maps, character art → `Shared/Maps/` or `Shared/Images/`
- Reference both from EN and PT content
- Mapas, mapas de batalha, arte de personagens → `Shared/Maps/` ou `Shared/Images/`
- Referencie de conteúdo EN e PT

### Folder Structure / Estrutura de Pastas
```
curse-of-strahd/
├── Home.md (English index)
├── Home-PT.md (Portuguese index)  
├── EN/ (English content)
│   ├── Characters/
│   ├── Locations/
│   ├── Templates/
│   └── ...
├── PT/ (Portuguese content)
│   ├── Characters/
│   ├── Locations/
│   ├── Templates/
│   └── ...
└── Shared/ (Language-neutral)
    ├── Maps/
    ├── Images/
    └── _attachments/
```

---
**Tags:** #guide #multi-language #setup