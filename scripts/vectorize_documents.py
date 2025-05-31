#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de vectorisation des documents pour AMDEC & Gamme IA
Peut être exécuté indépendamment pour indexer/réindexer la base vectorielle
"""

import os
import sys
import logging
import argparse
from datetime import datetime

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag import RAGEngine, DocumentProcessor, VectorStore

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('vectorization.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Fonction principale du script"""
    parser = argparse.ArgumentParser(description="Vectorisation des documents AMDEC & Gamme IA")
    
    parser.add_argument(
        '--documents-dir', 
        default='data/documents',
        help='Répertoire contenant les documents à vectoriser'
    )
    
    parser.add_argument(
        '--vector-db-path',
        default='data/vector_db', 
        help='Chemin de la base vectorielle ChromaDB'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force la réindexation complète même si la base existe'
    )
    
    parser.add_argument(
        '--test-mode',
        action='store_true',
        help='Mode test : vectorise seulement quelques documents'
    )
    
    parser.add_argument(
        '--clear',
        action='store_true', 
        help='Vide la base vectorielle existante'
    )
    
    args = parser.parse_args()
    
    logger.info("🚀 Démarrage de la vectorisation des documents")
    logger.info(f"📁 Répertoire documents: {args.documents_dir}")
    logger.info(f"🗄️ Base vectorielle: {args.vector_db_path}")
    
    try:
        # Créer les répertoires nécessaires
        os.makedirs(args.documents_dir, exist_ok=True)
        os.makedirs(args.vector_db_path, exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # Initialiser les composants
        logger.info("🔧 Initialisation des composants...")
        
        document_processor = DocumentProcessor(args.documents_dir)
        vector_store = VectorStore(args.vector_db_path)
        
        # Mode clear
        if args.clear:
            logger.info("🧹 Nettoyage de la base vectorielle...")
            if vector_store.clear_collection():
                logger.info("✅ Base vectorielle vidée")
            else:
                logger.error("❌ Erreur lors du nettoyage")
                return 1
        
        # Vérifier l'état actuel
        stats = vector_store.get_collection_stats()
        current_docs = stats.get('total_documents', 0)
        
        logger.info(f"📊 État actuel: {current_docs} documents dans la base")
        
        # Décider si vectorisation nécessaire
        needs_vectorization = (
            args.force or 
            current_docs == 0 or
            should_update_index(args.documents_dir, current_docs)
        )
        
        if not needs_vectorization and not args.clear:
            logger.info("✅ Base vectorielle à jour, aucune action nécessaire")
            logger.info("💡 Utilisez --force pour forcer la réindexation")
            return 0
        
        # Traiter les documents
        logger.info("📚 Traitement des documents...")
        documents = document_processor.process_all_documents()
        
        if not documents:
            logger.warning("⚠️ Aucun document trouvé ou traité")
            logger.info("💡 Placez vos documents dans le répertoire 'data/documents/'")
            logger.info("📋 Formats supportés: .docx, .pdf, .xlsx, .md, .txt")
            return 0
        
        logger.info(f"📄 {len(documents)} extraits de documents traités")
        
        # Mode test : limiter le nombre de documents
        if args.test_mode:
            test_limit = 10
            documents = documents[:test_limit]
            logger.info(f"🧪 Mode test : limitation à {len(documents)} extraits")
        
        # Nettoyage si force ou réindexation
        if args.force and current_docs > 0:
            logger.info("🧹 Réindexation complète : nettoyage de la base existante...")
            vector_store.clear_collection()
        
        # Vectorisation
        logger.info("🔄 Démarrage de la vectorisation...")
        start_time = datetime.now()
        
        success = vector_store.add_documents(documents)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        if success:
            # Statistiques finales
            final_stats = vector_store.get_collection_stats()
            final_docs = final_stats.get('total_documents', 0)
            
            logger.info("✅ Vectorisation terminée avec succès !")
            logger.info(f"📊 Résultats:")
            logger.info(f"   • Documents traités: {len(documents)}")
            logger.info(f"   • Total en base: {final_docs}")
            logger.info(f"   • Durée: {duration:.1f} secondes")
            logger.info(f"   • Sources: {', '.join(final_stats.get('sample_sources', []))}")
            
            # Test de recherche
            logger.info("🔍 Test de recherche...")
            test_results = vector_store.search("corrosion économiseur", n_results=3)
            if test_results:
                logger.info(f"✅ Test réussi: {len(test_results)} résultats trouvés")
                logger.info(f"   • Meilleur résultat (similarité {test_results[0]['similarity']:.3f}): {test_results[0]['content'][:100]}...")
            else:
                logger.warning("⚠️ Test de recherche sans résultat")
            
            return 0
            
        else:
            logger.error("❌ Échec de la vectorisation")
            return 1
            
    except KeyboardInterrupt:
        logger.info("⚠️ Vectorisation interrompue par l'utilisateur")
        return 1
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la vectorisation: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return 1

def should_update_index(documents_dir: str, current_docs: int) -> bool:
    """Détermine si l'index doit être mis à jour"""
    try:
        # Compter les fichiers documents
        doc_files = []
        
        if os.path.exists(documents_dir):
            for root, dirs, files in os.walk(documents_dir):
                for file in files:
                    if any(file.endswith(ext) for ext in ['.docx', '.pdf', '.xlsx', '.md', '.txt']):
                        doc_files.append(file)
        
        doc_count = len(doc_files)
        
        # Heuristique : si plus de fichiers que d'entrées vectorielles (ratio 5:1)
        expected_entries = doc_count * 5  # Estimation moyenne d'extraits par document
        
        logger.info(f"📁 Fichiers documents trouvés: {doc_count}")
        logger.info(f"📊 Entrées vectorielles attendues: ~{expected_entries}")
        logger.info(f"🗄️ Entrées actuelles en base: {current_docs}")
        
        return current_docs < expected_entries * 0.5  # Seuil à 50% des entrées attendues
        
    except Exception as e:
        logger.warning(f"Erreur évaluation mise à jour: {e}")
        return True  # En cas de doute, mettre à jour

def create_sample_documents():
    """Crée des documents d'exemple pour les tests"""
    docs_dir = 'data/documents'
    os.makedirs(docs_dir, exist_ok=True)
    
    # Document exemple 1: Guide AMDEC
    sample_amdec = """# Guide AMDEC - Chaudières Industrielles

## Économiseur Basse Température (BT)

### Épingle
- **Fonction**: Transfert thermique entre fumées et eau d'alimentation
- **Défaillances courantes**: 
  - Corrosion externe (F=3, G=4, D=2, C=24)
  - Encrassement interne réduisant l'efficacité
- **Actions préventives**: Revêtement céramique, contrôle qualité eau

### Collecteur de sortie
- **Fonction**: Collecte de la vapeur produite
- **Défaillances courantes**:
  - Caustic attack (F=3, G=5, D=3, C=45)
  - Fissuration par contraintes thermiques
- **Actions préventives**: Traitement chimique eau, inspection endoscopique

## Surchauffeur Haute Température (HT)

### Tube porteur
- **Fonction**: Support des contraintes mécaniques et thermiques
- **Défaillances courantes**:
  - Long-term overheat (F=2, G=5, D=3, C=30)
  - Rupture par fluage
- **Actions préventives**: Surveillance température continue, analyse métallurgique
"""
    
    with open(os.path.join(docs_dir, 'guide_amdec_example.md'), 'w', encoding='utf-8') as f:
        f.write(sample_amdec)
    
    logger.info("📝 Document d'exemple créé: guide_amdec_example.md")

if __name__ == "__main__":
    # Vérifier la présence de documents, sinon créer un exemple
    if not os.path.exists('data/documents') or len(os.listdir('data/documents')) == 0:
        logger.info("📝 Aucun document trouvé, création d'un exemple...")
        create_sample_documents()
    
    # Exécuter le script principal
    exit_code = main()
    sys.exit(exit_code)