import re
import os

class CobolMerger:

    def __init__(self):
        self.clubbed_set = dict()
        self.files_to_exclude = set()
        self.raw_clubbed_set = dict()

    def generate_club_pairs(self, file: [str], tech: str):
        if tech and tech.lower() == 'cobol':
            file_name = file[0].split('skel')[0].strip().split('src')[0].strip()
            if 'src' in file[0]:
                if file_name not in self.raw_clubbed_set:
                    self.raw_clubbed_set[file_name] = [None] * 2
                self.raw_clubbed_set.get(file_name)[0] = file

            elif 'skel' in file[0]:
                if file_name not in self.raw_clubbed_set:
                    self.raw_clubbed_set[file_name] = [None] * 2
                self.raw_clubbed_set.get(file_name)[1] = file

            if (file_name in self.raw_clubbed_set
                    and self.raw_clubbed_set.get(file_name)[0] is not None
                    and self.raw_clubbed_set.get(file_name)[1] is not None):
                self.clubbed_set[file_name] = self.raw_clubbed_set.get(file_name)

    def is_not_a_comment(self,line_: str):
        line_ = line_[6:72].strip()
        return not (line_.strip().startswith('/') or line_.strip().startswith('*') or line_.strip().startswith('==='))

    def create_merge_file(self):
        for clubbed_name,cobol_pairs in self.clubbed_set.items():
            src_path = os.path.join(cobol_pairs[0][1], cobol_pairs[0][0])
            skel_path = os.path.join(cobol_pairs[1][1], cobol_pairs[1][0])

            with open(src_path,'r') as src_file,open(skel_path, 'r') as skel_file:
                skel = 0
                src = 0
                src_ = src_file.read().splitlines()
                skel_ = skel_file.read().splitlines()

                for line in src_:
                    src += 1
                    pattern = r'.*?WORKING-STORAGE.*?'
                    match = re.findall(pattern, line)
                    if match and self.is_not_a_comment(line):
                        break

                clubbed = []

                for line in skel_:
                    skel += 1
                    pattern = r'.*?LINKAGE SECTION.*?'
                    match = re.findall(pattern, line)
                    if match and self.is_not_a_comment(line):
                        break
                    clubbed.append(line)

                next_ = ''
                for i in range(src, len(src_)):
                    src += 1
                    pattern = r'.*?LINKAGE SECTION.*?'
                    match = re.findall(pattern, src_[i])
                    if self.is_not_a_comment(src_[i]) and match:
                        next_ = src_[src][6:72].split('.')[0].strip()
                        break
                    clubbed.append(src_[i])

                for i in range(skel, len(skel_)):
                    if next_ and self.is_not_a_comment(skel_[i]):
                        pattern = f'.*?{next_}.*?'
                        match = re.findall(pattern, skel_[i])
                        if match:
                            break
                    clubbed.append(skel_[i])
                    skel += 1

                src += 2  # done to remove the first procedure_para

                for i in range(src, len(src_)):
                    src += 1
                    clubbed.append(src_[i])

                for i in range(skel, len(skel_)):
                    skel += 1
                    clubbed.append(skel_[i])

                clubbed = '\n'.join(line for line in clubbed)
                self.create_and_write_file(cobol_pairs[0][1], f'{clubbed_name} listing.txt', clubbed)
                self.files_to_exclude.add(src_path)
                self.files_to_exclude.add(skel_path)

    def create_and_write_file(self, dir, file_name, content):
        file_path = os.path.join(dir, file_name)
        if file_name in os.listdir(dir):
            os.remove(file_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        try:
            with open(file_path, 'w') as file:
                file.write(content)
            print(f"{file_name} created successfully at: {file_path}")
        except Exception as e:
            print(f"Error creating or writing to file for {file_name}: {e}")

