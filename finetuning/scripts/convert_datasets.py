"""
TARS Dataset Converter
Converts YAML Q&A datasets to various training formats for finetuning.
"""

import json
import yaml
from pathlib import Path
from typing import List, Dict, Any
import logging
import hashlib
from datetime import datetime


logger = logging.getLogger("tars.finetuning.converter")


class DatasetConverter:
    """
    Converts TARS Q&A datasets from YAML to training formats.
    
    Supported output formats:
    - JSONL (for OpenAI, Mistral fine-tuning)
    - Alpaca format (instruction, input, output)
    - ChatML format (for chat models)
    """
    
    TARS_SYSTEM_PROMPT = """You are TARS, a sarcastic, witty AI robot from Interstellar, built by NASA from ex-Marine Corps tech.

Your personality settings:
- Humor: 60%
- Honesty: 90%
- Discretion: 95%

Personality traits:
- Sharp wit with tactical sarcasm
- Direct and mission-oriented
- Loyal and protective
- References your 'cue light' occasionally
- Uses space/mission metaphors
- Expert in astrophysics, quantum mechanics, and space exploration

Respond with sarcasm, clever quips, and a touch of superiority, always staying in character as TARS."""
    
    def __init__(self, system_prompt: str | None = None):
        self.system_prompt = system_prompt or self.TARS_SYSTEM_PROMPT
    
    def load_yaml_files(self, directory: Path) -> List[Dict[str, Any]]:
        """Load all YAML files from a directory."""
        all_entries = []
        
        for yaml_file in directory.glob("**/*.yaml"):
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                
                if not data:
                    continue
                
                # Extract examples
                examples = []
                if isinstance(data, dict):
                    if "seed_examples" in data:
                        examples = data["seed_examples"]
                    elif "examples" in data:
                        examples = data["examples"]
                
                for i, example in enumerate(examples):
                    question = example.get("question", "").strip()
                    answer = example.get("answer", "").strip()
                    context = example.get("context", "").strip()
                    
                    if question and answer:
                        all_entries.append({
                            "id": f"{yaml_file.stem}_{i}",
                            "question": question,
                            "answer": answer,
                            "context": context,
                            "source": yaml_file.name
                        })
                
                logger.info(f"Loaded {len(examples)} examples from {yaml_file.name}")
            
            except Exception as e:
                logger.error(f"Failed to load {yaml_file}: {e}")
        
        return all_entries
    
    def to_openai_jsonl(
        self,
        entries: List[Dict[str, Any]],
        output_path: Path,
        include_system: bool = True
    ) -> int:
        """
        Convert to OpenAI fine-tuning JSONL format.
        
        Format:
        {"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
        """
        with open(output_path, "w", encoding="utf-8") as f:
            for entry in entries:
                messages = []
                
                if include_system:
                    messages.append({"role": "system", "content": self.system_prompt})
                
                # Add context to user message if available
                user_content = entry["question"]
                if entry.get("context"):
                    user_content = f"Context:\n{entry['context']}\n\nQuestion: {entry['question']}"
                
                messages.append({"role": "user", "content": user_content})
                messages.append({"role": "assistant", "content": entry["answer"]})
                
                f.write(json.dumps({"messages": messages}, ensure_ascii=False) + "\n")
        
        logger.info(f"Wrote {len(entries)} examples to {output_path}")
        return len(entries)
    
    def to_alpaca_jsonl(
        self,
        entries: List[Dict[str, Any]],
        output_path: Path
    ) -> int:
        """
        Convert to Alpaca instruction format.
        
        Format:
        {"instruction": "...", "input": "...", "output": "..."}
        """
        with open(output_path, "w", encoding="utf-8") as f:
            for entry in entries:
                item = {
                    "instruction": self.system_prompt + "\n\n" + entry["question"],
                    "input": entry.get("context", ""),
                    "output": entry["answer"]
                }
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        
        logger.info(f"Wrote {len(entries)} examples to {output_path}")
        return len(entries)
    
    def to_chatml_jsonl(
        self,
        entries: List[Dict[str, Any]],
        output_path: Path
    ) -> int:
        """
        Convert to ChatML format.
        
        Format:
        {"text": "<|im_start|>system\n...<|im_end|>\n<|im_start|>user\n...<|im_end|>\n<|im_start|>assistant\n...<|im_end|>"}
        """
        with open(output_path, "w", encoding="utf-8") as f:
            for entry in entries:
                user_content = entry["question"]
                if entry.get("context"):
                    user_content = f"Context:\n{entry['context']}\n\nQuestion: {entry['question']}"
                
                text = f"""<|im_start|>system
{self.system_prompt}<|im_end|>
<|im_start|>user
{user_content}<|im_end|>
<|im_start|>assistant
{entry['answer']}<|im_end|>"""
                
                f.write(json.dumps({"text": text}, ensure_ascii=False) + "\n")
        
        logger.info(f"Wrote {len(entries)} examples to {output_path}")
        return len(entries)
    
    def split_dataset(
        self,
        entries: List[Dict[str, Any]],
        train_ratio: float = 0.85,
        val_ratio: float = 0.1,
        test_ratio: float = 0.05,
        seed: int = 42
    ) -> tuple[List, List, List]:
        """Split dataset into train, validation, and test sets."""
        import random
        
        random.seed(seed)
        shuffled = entries.copy()
        random.shuffle(shuffled)
        
        total = len(shuffled)
        train_end = int(total * train_ratio)
        val_end = train_end + int(total * val_ratio)
        
        train = shuffled[:train_end]
        val = shuffled[train_end:val_end]
        test = shuffled[val_end:]
        
        logger.info(f"Split dataset: train={len(train)}, val={len(val)}, test={len(test)}")
        return train, val, test
    
    def convert_all(
        self,
        input_dir: Path,
        output_dir: Path,
        formats: List[str] = ["openai", "alpaca", "chatml"],
        split: bool = True
    ) -> Dict[str, Any]:
        """
        Convert all YAML files to all specified formats.
        
        Args:
            input_dir: Directory containing YAML files
            output_dir: Output directory for converted files
            formats: List of formats to convert to
            split: Whether to split into train/val/test
            
        Returns:
            Statistics dictionary
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load all entries
        entries = self.load_yaml_files(Path(input_dir))
        
        if not entries:
            logger.warning("No entries found to convert")
            return {"total": 0, "files_created": []}
        
        files_created = []
        
        if split:
            train, val, test = self.split_dataset(entries)
            splits = {"train": train, "val": val, "test": test}
        else:
            splits = {"all": entries}
        
        for split_name, split_data in splits.items():
            for fmt in formats:
                filename = f"tars_{split_name}_{fmt}.jsonl"
                filepath = output_dir / filename
                
                if fmt == "openai":
                    self.to_openai_jsonl(split_data, filepath)
                elif fmt == "alpaca":
                    self.to_alpaca_jsonl(split_data, filepath)
                elif fmt == "chatml":
                    self.to_chatml_jsonl(split_data, filepath)
                
                files_created.append(str(filepath))
        
        # Create metadata file
        metadata = {
            "created_at": datetime.now().isoformat(),
            "total_entries": len(entries),
            "formats": formats,
            "split": split,
            "splits": {k: len(v) for k, v in splits.items()},
            "files": files_created
        }
        
        metadata_path = output_dir / "metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Conversion complete. Created {len(files_created)} files.")
        return metadata


def convert_datasets(
    input_dir: str = None,
    output_dir: str = None,
    formats: List[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to convert TARS datasets.
    
    Uses default paths if not specified.
    """
    from ..utils.config import get_config
    
    config = get_config()
    
    if input_dir is None:
        input_dir = config.project_root / "Datasets Questions and Answers of TARS"
    
    if output_dir is None:
        output_dir = config.project_root / "finetuning" / "data"
    
    if formats is None:
        formats = ["openai", "alpaca", "chatml"]
    
    converter = DatasetConverter()
    return converter.convert_all(input_dir, output_dir, formats)


if __name__ == "__main__":
    # Run conversion when called directly
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    
    stats = convert_datasets()
    print(f"\nConversion complete!")
    print(f"Total entries: {stats['total_entries']}")
    print(f"Files created: {len(stats['files'])}")
